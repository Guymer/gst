#!/usr/bin/env python3

# Define function ...
def sail(lon, lat, spd, /, *, cons = 2.0, dur = 1.0, freqLand = 100, freqPlot = 25, freqSimp = 25, local = False, nang = 9, plot = False, prec = 10000.0, res = "c", tol = 1.0e-10):
    """Sail from a point

    This function reads in a starting coordinate (in degrees) and a sailing
    speed (in knots) and then calculates the maximum possible sailing distance
    on the surface of the Earth that the vessel can reach in the specified time.

    Parameters
    ----------
    lon : float
        the longitude of the starting point (in degrees)
    lat : float
        the latitude of the starting point (in degrees)
    spd : float
        the speed of the vessel (in knots)
    cons : float, optional
        the amount of conservatism to add to the calculation
    dur : float, optional
        the duration of the voyage (in days)
    freqLand : int, optional
        re-evaluate the relevant land every freqLand iteration
    freqPlot : int, optional
        plot sailing contours every freqPlot iteration
    freqSimp : int, optional
        simplify the sailing contour every freqSimp iteration
    local : bool, optional
        the plot has only local extent
    nang : int, optional
        the number of directions from each point that the vessel could sail in
    plot : bool, optional
        make a plot
    prec : float, optional
        the precision of the calculation (in metres)
    res : string, optional
        the resolution of the Global Self-Consistent Hierarchical
        High-Resolution Geography datasets
    tol : float, optional
        the Euclidean distance that defines two points as being the same (in
        degrees)
    """

    # Import standard modules ...
    import gzip
    import math
    import os
    import time

    # Import special modules ...
    try:
        import cartopy
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                   "backend" : "Agg",                                           # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
                "figure.dpi" : 300,
                 "font.size" : 8,
            }
        )
        import matplotlib.pyplot
    except:
        raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
    try:
        import shapely
        import shapely.geometry
        import shapely.ops
        import shapely.wkb
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
        import pyguymer3.image
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # Import sub-functions ...
    from .removeInteriorRingsWhichAreLand import removeInteriorRingsWhichAreLand
    from .removeLands import removeLands
    from .saveAllCanals import saveAllCanals
    from .saveAllLands import saveAllLands
    from .saveRelevantLands import saveRelevantLands

    # **************************************************************************

    print(f"{spd:,.1f} knots is {0.001 * 1852.0 * spd:,.2f} kilometres/hour.")
    print(f"{spd:,.1f} knots is {0.001 * 24.0 * 1852.0 * spd:,.2f} kilometres/day.")

    # Determine how many degrees (of longitude) a [Multi]Polygon can be
    # filled by at the point where a degree (of longitude) is the largest, i.e.,
    # the equator ...
    # NOTE: See https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
    # NOTE: Using a radius of 6,371,008.8 m equates to:
    #         * 1 °  = 111.195 km
    #         * 1 m° = 111.195 m
    #         * 1 μ° = 11.1195 cm
    radiusOfEarth = 6371008.8                                                   # [m]
    circumOfEarth = 2.0 * math.pi * radiusOfEarth                               # [m]
    resoluOfEarth = circumOfEarth / 360.0                                       # [m/°]
    fill = prec / resoluOfEarth                                                 # [°]

    # Add conservatism ...
    fill /= cons                                                                # [°]

    # Use fill level to set the simplification level ...
    simp = fill / cons                                                          # [°]

    # Find the distance straight up and down to the North and South Poles ...
    toNorthPole, _, _ = pyguymer3.geo.calc_dist_between_two_locs(
        lon,
        lat,
        lon,
        +90.0,
    )                                                                           # [m], [°], [°]
    toSouthPole, _, _ = pyguymer3.geo.calc_dist_between_two_locs(
        lon,
        lat,
        lon,
        -90.0,
    )                                                                           # [m], [°], [°]

    print(f"The North Pole is {0.001 * toNorthPole:,.2f} kilometres up (ignoring all land).")
    print(f"The South Pole is {0.001 * toSouthPole:,.2f} kilometres down (ignoring all land).")

    # Create the initial starting Point ...
    ship = shapely.geometry.point.Point(lon, lat)

    # Calculate the maximum possible sailing distance (ignoring all land) ...
    # NOTE: If the distance is very large then the ship can sail anywhere.
    maxDist = (1852.0 * spd) * (24.0 * dur)                                     # [m]
    if maxDist > 19970326.3:
        maxShip = pyguymer3.geo.fillin(
            shapely.geometry.polygon.orient(
                shapely.geometry.polygon.Polygon(
                    shapely.geometry.polygon.LinearRing(
                        [
                            (-180.0,  90.0),
                            (+180.0,  90.0),
                            (+180.0, -90.0),
                            (-180.0, -90.0),
                            (-180.0,  90.0),
                        ]
                    )
                )
            ),
            +1.0,
            tol = tol,
        )
    else:
        maxShip = pyguymer3.geo.buffer(
            ship,
            maxDist,
            fill = +1.0,
            nang = 361,
            simp = -1.0,
             tol = tol,
        )
    maxShipExt = [
        maxShip.bounds[0],              # minx
        maxShip.bounds[2],              # maxx
        maxShip.bounds[1],              # miny
        maxShip.bounds[3],              # maxy
    ]                                                                           # [°]

    # Check if the user wants a local plot (for local people) ...
    if local:
        # Determine the maximum symmetric sailing distance ...
        maxShipLon = max(abs(maxShipExt[0] - lon), abs(maxShipExt[1] - lon))    # [°]
        maxShipLat = max(abs(maxShipExt[2] - lat), abs(maxShipExt[3] - lat))    # [°]
        maxShipHyp = max(maxShipLon, maxShipLat)                                # [°]
        maxShipExtSym = [
            lon - maxShipHyp,           # minx
            lon + maxShipHyp,           # maxx
            lat - maxShipHyp,           # miny
            lat + maxShipHyp,           # maxy
        ]                                                                       # [°]

    # Check if the user is being far too coarse ...
    if prec > maxDist:
        raise Exception(f"the maximum possible sailing distance is {0.001 * maxDist:,.2f} kilometres but the precision is {0.001 * prec:,.2f} kilometres") from None

    print(f"The maximum possible sailing distance is {0.001 * maxDist:,.2f} kilometres (ignoring all land).")

    # Figure out how many steps are going to be required ...
    nstep = round(maxDist / prec)                                               # [#]

    print(f"Each sailing iteration is {prec / (24.0 * 1852.0 * spd):,.4f} days for the vessel.")

    # **************************************************************************

    # Determine first output folder name and make it if it is missing ...
    output1 = f"res={res}_cons={cons:.2e}_tol={tol:.2e}"
    if not os.path.exists(output1):
        os.mkdir(output1)
    if not os.path.exists(f"{output1}/allLands"):
        os.mkdir(f"{output1}/allLands")

    # Determine second output folder name and make it if it is missing ...
    output2 = f"{output1}/nang={nang:d}_prec={prec:.2e}"
    if not os.path.exists(output2):
        os.mkdir(output2)
    if not os.path.exists(f"{output2}/allLands"):
        os.mkdir(f"{output2}/allLands")

    # Determine third output folder name and make it if it is missing ...
    output3 = f"{output2}/freqLand={freqLand:d}_freqSimp={freqSimp:d}_lon={lon:+011.6f}_lat={lat:+010.6f}"
    if not os.path.exists(output3):
        os.mkdir(output3)
    if not os.path.exists(f"{output3}/limit"):
        os.mkdir(f"{output3}/limit")
    if not os.path.exists(f"{output3}/relevantLands"):
        os.mkdir(f"{output3}/relevantLands")
    if not os.path.exists(f"{output3}/ship"):
        os.mkdir(f"{output3}/ship")

    # **************************************************************************

    # Deduce filename ...
    allLandsName = f"{output1}/allLands.wkb.gz"

    # Check if the file is missing ...
    if not os.path.exists(allLandsName):
        print(f"Making \"{allLandsName}\" ...", end = " ")

        # Start timer ...
        start = time.time()                                                     # [s]

        # Make the compressed WKB file of all of the land ...
        # NOTE: This is an un-buffered dataset without canals that is used
        #       purely for visualisation by other scripts.
        savedAllLands = saveAllLands(
            allLandsName,
            f"{output1}/allLands",
             debug = False,
            levels = (1, 5, 6),
               res = res,
              simp = simp,
               tol = tol,
        )

        # Print timer ...
        print(f"took {time.time() - start:,.2f} seconds.")

    # **************************************************************************

    # Deduce input filename ...
    allCanalsName = f"{output1}/allCanals.wkb.gz"

    # Check if the input file is missing ...
    if not os.path.exists(allCanalsName):
        print(f"Making \"{allCanalsName}\" ...", end = " ")

        # Start timer ...
        start = time.time()                                                     # [s]

        # Make the compressed WKB file of all of the canals ...
        savedAllCanals = saveAllCanals(
            allCanalsName,
            debug = False,
             simp = simp,
              tol = tol,
        )

        # Print timer ...
        print(f"took {time.time() - start:,.2f} seconds.")
    else:
        # Set flag (if the file exists then canals must have been saved) ...
        savedAllCanals = True

    # Load all the canals ...
    # NOTE: Given how "allCanals" was made, we know that there aren't any
    #       invalid LineStrings, so don't bother checking for them.
    if savedAllCanals:
        with gzip.open(allCanalsName, mode = "rb") as gzObj:
            allCanals = pyguymer3.geo.extract_lines(shapely.wkb.loads(gzObj.read()), onlyValid = False)
    else:
        allCanals = None

    # **************************************************************************

    # Deduce input filename ...
    allLandsName = f"{output2}/allLands.wkb.gz"

    # Check if the input file is missing ...
    if not os.path.exists(allLandsName):
        print(f"Making \"{allLandsName}\" ...", end = " ")

        # Start timer ...
        start = time.time()                                                     # [s]

        # Make the compressed WKB file of all of the land ...
        savedAllLands = saveAllLands(
            allLandsName,
            f"{output2}/allLands",
            allCanals = allCanals,
                debug = False,
                 dist = prec,
                 fill = fill,
               levels = (1, 5, 6),
                 nang = nang,
                  res = res,
                 simp = simp,
                  tol = tol,
        )

        # Print timer ...
        print(f"took {time.time() - start:,.2f} seconds.")
    else:
        # Set flag (if the file exists then land must have been saved) ...
        savedAllLands = True

    # Load all the land ...
    # NOTE: Given how "allLands" was made, we know that there aren't any invalid
    #       Polygons, so don't bother checking for them.
    if savedAllLands:
        with gzip.open(allLandsName, mode = "rb") as gzObj:
            allLands = pyguymer3.geo.extract_polys(shapely.wkb.loads(gzObj.read()), onlyValid = False, repair = False)
    else:
        allLands = None

    # **************************************************************************

    # Check that the ship is not starting on any land ...
    for allLand in allLands:
        if allLand.contains(ship):
            raise Exception("the ship is starting on land") from None

    # **************************************************************************

    # Check if the user wants to make a plot ...
    if plot:
        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (9, 6))

        # Check if the user wants a local plot (for local people) ...
        if local:
            # Create axis ...
            ax = fg.add_subplot(
                projection = cartopy.crs.Orthographic(
                    central_longitude = lon,
                     central_latitude = lat,
                ),
            )

            # Configure axis ...
            ax.set_extent(maxShipExt)
            pyguymer3.geo.add_horizontal_gridlines(
                ax,
                maxShipExtSym,
                locs = range(-90, 100, 10),
            )
            pyguymer3.geo.add_vertical_gridlines(
                ax,
                maxShipExtSym,
                locs = range(-180, 190, 10),
            )
        else:
            # Create axis ...
            ax = fg.add_subplot(projection = cartopy.crs.Robinson())

            # Configure axis ...
            ax.set_global()
            pyguymer3.geo.add_horizontal_gridlines(
                ax,
                [-180.0, +180.0, -90.0, +90.0],
                locs = range(-90, 135, 45),
            )
            pyguymer3.geo.add_vertical_gridlines(
                ax,
                [-180.0, +180.0, -90.0, +90.0],
                locs = range(-180, 225, 45),
            )

        # Configure axis ...
        pyguymer3.geo.add_map_background(ax, resolution = "large8192px")

        # Plot Polygons ...
        ax.add_geometries(
            allLands,
            cartopy.crs.PlateCarree(),
            edgecolor = (1.0, 0.0, 0.0, 0.2),
            facecolor = (1.0, 0.0, 0.0, 0.2),
            linewidth = 1.0,
        )

        # Plot Polygons ...
        # NOTE: Given how "maxShip" was made, we know that there aren't any
        #       invalid Polygons, so don't bother checking for them.
        ax.add_geometries(
            pyguymer3.geo.extract_polys(maxShip, onlyValid = False, repair = False),
            cartopy.crs.PlateCarree(),
            edgecolor = (0.0, 0.0, 0.0, 0.2),
            facecolor = (0.0, 0.0, 0.0, 0.2),
            linewidth = 1.0,
        )

    # **************************************************************************

    # Initialize area ...
    oldArea = 0.0                                                               # [°2]

    # Loop over iterations ...
    for istep in range(nstep):
        print(f"Iteration {istep + 1:,d}/{nstep:,d} ({0.001 * (istep + 1) * prec:,.2f} kilometres/{(istep + 1) * prec / (24.0 * 1852.0 * spd):,.4f} days of sailing) ...")

        # **********************************************************************

        # Check if this step needs the list of relevant land updating ...
        if istep % freqLand == 0:
            print(" > Re-evaluating the relevant land ...")

            # Deduce input filename ...
            relevantLandsName = f"{output3}/relevantLands/istep={istep:06d}.wkb.gz"

            # Check if the input file is missing ...
            if not os.path.exists(relevantLandsName):
                print(f"   Making \"{relevantLandsName}\" ...", end = " ")

                # Start timer ...
                start = time.time()                                             # [s]

                # Make the compressed WKB file of all of the relevant land ...
                savedRelevantLands = saveRelevantLands(
                    relevantLandsName,
                    ship,
                    cons * freqLand * prec,
                    allLands,
                    fill = +1.0,
                    nang = 361,
                    simp = -1.0,
                     tol = tol,
                )

                # Print timer ...
                print(f"took {time.time() - start:,.2f} seconds.")
            else:
                # Set flag (if the file exists then land must have been saved) ...
                savedRelevantLands = True

            # Load all the relevant land ...
            # NOTE: Given how "relevantLands" was made, we know that there
            #       aren't any invalid Polygons, so don't bother checking for
            #       them.
            if savedRelevantLands:
                with gzip.open(relevantLandsName, mode = "rb") as gzObj:
                    relevantLands = pyguymer3.geo.extract_polys(shapely.wkb.loads(gzObj.read()), onlyValid = False, repair = False)
            else:
                relevantLands = None

        # **********************************************************************

        # Deduce temporary file name and skip if it exists already ...
        tname = f"{output3}/ship/istep={istep:06d}.wkb.gz"
        if os.path.exists(tname):
            # Load [Multi]Polygon ...
            with gzip.open(tname, mode = "rb") as gzObj:
                ship = shapely.wkb.loads(gzObj.read())
        else:
            # Check what type the ship is currently ...
            if isinstance(ship, shapely.geometry.point.Point):
                # Create copy of the ship ...
                limit = shapely.geometry.point.Point(lon, lat)
            else:
                # Start timer ...
                start = time.time()                                             # [s]

                # Extract the current limit of sailing (on water) ...
                # NOTE: Given how "ship" was made, we know that there aren't any
                #       invalid Polygons, so don't bother checking for them.
                limit = []
                for poly in pyguymer3.geo.extract_polys(ship, onlyValid = False, repair = False):
                    limit += pyguymer3.geo.extract_lines(
                        removeLands(
                            poly.exterior,
                            relevantLands,
                            debug = False,
                             simp = -1.0,
                        ),
                        onlyValid = False,
                    )
                    for interior in poly.interiors:
                        limit += pyguymer3.geo.extract_lines(
                            removeLands(
                                interior,
                                relevantLands,
                                debug = False,
                                 simp = -1.0,
                            ),
                            onlyValid = False,
                        )
                limit = shapely.geometry.multilinestring.MultiLineString(limit)

                print(f" > removed/unioned in {time.time() - start:,.2f} seconds.")

                # Save [Multi]LineString ...
                with gzip.open(f"{output3}/limit/istep={istep:06d}.wkb.gz", mode = "wb", compresslevel = 9) as gzObj:
                    gzObj.write(shapely.wkb.dumps(limit))

            # ******************************************************************

            # Find out how many points describe this [Multi]LineString ...
            # NOTE: Given how "limit" was made, we know that there aren't any
            #       invalid LineStrings, so don't bother checking for them.
            nline = 0                                                           # [#]
            npoint = 0                                                          # [#]
            for line in pyguymer3.geo.extract_lines(limit, onlyValid = False):
                nline += 1                                                      # [#]
                npoint += len(line.coords)                                      # [#]

            print(f" > \"limit\" is described by {npoint:,d} Points in {nline:,d} LineStrings.")
            print(f"   The x-bound is {limit.bounds[0]:+011.6f}° ≤ longitude ≤ {limit.bounds[2]:+011.6f}°.")
            print(f"   The y-bound is {limit.bounds[1]:+010.6f}° ≤ latitude ≤ {limit.bounds[3]:+010.6f}°.")

            # ******************************************************************

            # Check if this step is simplifying ...
            if (istep + 1) % freqSimp == 0:
                # Start timer ...
                start = time.time()                                             # [s]

                # Sail ...
                limit = pyguymer3.geo.buffer(
                    limit,
                    prec,
                    fill = fill,
                    nang = nang,
                    simp = simp,
                     tol = tol,
                )
                ship = shapely.ops.unary_union([limit, ship])
                ship = removeLands(
                    ship,
                    relevantLands,
                    debug = False,
                     simp = simp,
                )
                ship = removeInteriorRingsWhichAreLand(
                    ship,
                    relevantLands,
                    onlyValid = False,
                         prec = prec / cons,
                       repair = False,
                )

                print(f" > filled/buffered/simplified/unioned/removed in {time.time() - start:,.2f} seconds.")
            else:
                # Start timer ...
                start = time.time()                                             # [s]

                # Sail ...
                limit = pyguymer3.geo.buffer(
                    limit,
                    prec,
                    fill = fill,
                    nang = nang,
                    simp = -1.0,
                     tol = tol,
                )
                ship = shapely.ops.unary_union([limit, ship])
                ship = removeLands(
                    ship,
                    relevantLands,
                    debug = False,
                     simp = -1.0,
                )
                ship = removeInteriorRingsWhichAreLand(
                    ship,
                    relevantLands,
                    onlyValid = False,
                         prec = prec / cons,
                       repair = False,
                )

                print(f" > filled/buffered/filled/unioned/removed in {time.time() - start:,.2f} seconds.")

            # Clean up ...
            del limit

            # Save [Multi]Polygon ...
            with gzip.open(tname, mode = "wb", compresslevel = 9) as gzObj:
                gzObj.write(shapely.wkb.dumps(ship))

        # **********************************************************************

        # Find out how many points describe this [Multi]Polygon ...
        # NOTE: Given how "ship" was made, we know that there aren't any invalid
        #       Polygons, so don't bother checking for them.
        npoint = 0                                                              # [#]
        npoly = 0                                                               # [#]
        for poly in pyguymer3.geo.extract_polys(ship, onlyValid = False, repair = False):
            npoint += len(poly.exterior.coords)                                 # [#]
            npoly += 1                                                          # [#]
            for interior in poly.interiors:
                npoint += len(interior.coords)                                  # [#]

        print(f" > \"ship\" is described by {npoint:,d} Points in {npoly:,d} Polygons.")
        print(f"   The x-bound is {ship.bounds[0]:+011.6f}° ≤ longitude ≤ {ship.bounds[2]:+011.6f}°.")
        print(f"   The y-bound is {ship.bounds[1]:+010.6f}° ≤ latitude ≤ {ship.bounds[3]:+010.6f}°.")

        # **********************************************************************

        # Check if the user wants to make a plot and that this iteration is one
        # of the ones to be plotted ...
        if plot and (istep + 1) % freqPlot == 0:
            print(" > Plotting ...")

            # Plot Polygons ...
            # NOTE: Given how "ship" was made, we know that there aren't any
            #       invalid Polygons, so don't bother checking for them.
            ax.add_geometries(
                pyguymer3.geo.extract_polys(ship, onlyValid = False, repair = False),
                cartopy.crs.PlateCarree(),
                edgecolor = f"C{((istep + 1) // freqPlot) - 1:d}",
                facecolor = "none",
                linewidth = 1.0,
            )

        # **********************************************************************

        # Check if the ship hasn't moved ...
        if (abs(ship.area - oldArea) / max(tol, oldArea)) < tol:
            print("WARNING: The ship hasn't moved, stopping sailing.")

            # Make sure that a plot isn't made as the user-requested duration
            # may differ from the actual sailed duration ...
            plot = False

            # Stop looping ...
            break

        # Update the area ...
        oldArea = ship.area                                                     # [°2]

    # **************************************************************************

    # Check if the user wants to make a plot ...
    if plot:
        # Determine output PNG file name ...
        png = f"{output3}/dur={dur:.2f}_local={repr(local)[0]}_freqPlot={freqPlot:d}_spd={spd:.1f}.png"

        print(f"Making \"{png}\" ...")

        # Configure figure ...
        fg.tight_layout()

        # Save figure ...
        fg.savefig(png)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimize_image(png, strip = True)
