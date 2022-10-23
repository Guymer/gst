def sail(lon, lat, spd, kwArgCheck = None, cons = 2.0, dur = 1.0, freqLand = 100, freqPlot = 25, freqSimp = 25, local = False, nang = 9, plot = False, prec = 10000.0, res = "c", tol = 1.0e-10):
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

    # Improt standard modules ...
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
        matplotlib.use("Agg")                                                   # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
        import matplotlib.pyplot
        matplotlib.pyplot.rcParams.update({"font.size" : 8})
    except:
        raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
    try:
        import shapely
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
    from .removeInteriorRings import removeInteriorRings
    from .removeLands import removeLands
    from .saveAllCanals import saveAllCanals
    from .saveAllLands import saveAllLands

    # Check keyword arguments ...
    if kwArgCheck is not None:
        print(f"WARNING: \"{__name__}\" has been called with an extra positional argument")

    # **************************************************************************

    print(f"{spd:,.1f} knots is {0.001 * 1852.0 * spd:,.2f} kilometres/hour.")
    print(f"{spd:,.1f} knots is {0.001 * 24.0 * 1852.0 * spd:,.2f} kilometres/day.")

    # Determine how many degrees (of longitude) a [Multi]Polygon can be
    # filled by at the point where a degree (of longitude) is the largest, i.e.,
    # the equator ...
    # NOTE: See https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
    # NOTE: These equate to:
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
    maxDist = (1852.0 * spd) * (24.0 * dur)                                     # [m]
    maxShip = pyguymer3.geo.buffer(
        ship,
        maxDist,
        fill = fill,
        nang = nang,
        simp = simp,
         tol = tol,
    )
    maxShipExt = [
        maxShip.bounds[0],              # minx
        maxShip.bounds[2],              # maxx
        maxShip.bounds[1],              # miny
        maxShip.bounds[3],              # maxy
    ]                                                                           # [°]

    # Determine the maximum symmetric sailing distance ...
    maxShipLon = max(abs(maxShipExt[0] - lon), abs(maxShipExt[1] - lon))        # [°]
    maxShipLat = max(abs(maxShipExt[2] - lat), abs(maxShipExt[3] - lat))        # [°]
    maxShipHyp = max(maxShipLon, maxShipLat)                                    # [°]
    maxShipExtSym = [
        lon - maxShipHyp,
        lon + maxShipHyp,
        lat - maxShipHyp,
        lat + maxShipHyp,
    ]                                                                           # [°]

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
    if not os.path.exists(f"{output3}/ship"):
        os.mkdir(f"{output3}/ship")

    # **************************************************************************

    # Deduce filename ...
    allLandsName = f"{output1}/allLands.wkb.gz"

    # Check if the file is missing ...
    if not os.path.exists(allLandsName):
        print(f"Making \"{allLandsName}\" ...")

        # Make the compressed WKB file of all of the land ...
        # NOTE: This is an un-buffered dataset without canals that is used
        #       purely for visualisation by other scripts.
        savedAllLands = saveAllLands(
            allLandsName,
            f"{output1}/allLands",
             res = res,
            simp = simp,
             tol = tol,
        )

    # **************************************************************************

    # Deduce input filename ...
    allCanalsName = f"{output1}/allCanals.wkb.gz"

    # Check if the input file is missing ...
    if not os.path.exists(allCanalsName):
        print(f"Making \"{allCanalsName}\" ...")

        # Make the compressed WKB file of all of the canals ...
        savedAllCanals = saveAllCanals(
            allCanalsName,
            debug = True,
             simp = simp,
              tol = tol,
        )
    else:
        # Set flag (if the file exists then canals must have been saved) ...
        savedAllCanals = True

    # Load all the canals ...
    if savedAllCanals:
        with gzip.open(allCanalsName, "rb") as fObj:
            allCanals = shapely.wkb.loads(fObj.read())
    else:
        allCanals = None

    # **************************************************************************

    # Deduce input filename ...
    allLandsName = f"{output2}/allLands.wkb.gz"

    # Check if the input file is missing ...
    if not os.path.exists(allLandsName):
        print(f"Making \"{allLandsName}\" ...")

        # Make the compressed WKB file of all of the land ...
        savedAllLands = saveAllLands(
            allLandsName,
            f"{output2}/allLands",
            allCanals = allCanals,
                 dist = prec,
                 fill = fill,
                 nang = nang,
                  res = res,
                 simp = simp,
                  tol = tol,
        )
    else:
        # Set flag (if the file exists then land must have been saved) ...
        savedAllLands = True

    # Load all the land ...
    if savedAllLands:
        with gzip.open(allLandsName, "rb") as fObj:
            allLands = shapely.wkb.loads(fObj.read())
    else:
        allLands = None

    # **************************************************************************

    # Check that the ship is not starting on any land ...
    if allLands.contains(ship):
        raise Exception("the ship is starting on land") from None

    # **************************************************************************

    # Check if the user wants to make a plot ...
    if plot:
        # Create figure ...
        fg = matplotlib.pyplot.figure(
                dpi = 300,
            figsize = (9, 6),
        )

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
            pyguymer3.geo.extract_polys(allLands),
            cartopy.crs.PlateCarree(),
            edgecolor = (1.0, 0.0, 0.0, 0.2),
            facecolor = (1.0, 0.0, 0.0, 0.2),
            linewidth = 1.0,
        )

        # Plot Polygons ...
        ax.add_geometries(
            pyguymer3.geo.extract_polys(maxShip),
            cartopy.crs.PlateCarree(),
            edgecolor = (0.0, 0.0, 0.0, 0.2),
            facecolor = (0.0, 0.0, 0.0, 0.2),
            linewidth = 1.0,
        )

    # **************************************************************************

    # Loop over iterations ...
    for istep in range(nstep):
        print(f"Iteration {istep + 1:,d}/{nstep:,d} ({0.001 * (istep + 1) * prec:,.2f} kilometres/{(istep + 1) * prec / (24.0 * 1852.0 * spd):,.4f} days of sailing) ...")

        # **********************************************************************

        # Check if this step needs the list of relevant land updating ...
        if istep % freqLand == 0:
            print(" > Re-evaluating the relevant land ...")

            # Initialize list ...
            relevantLands = []

            # Loop over Polygons in the MultiPolygon of all of the land ...
            for allLand in pyguymer3.geo.extract_polys(allLands):
                # Skip land which is outside of the maximum possible sailing
                # distance of the ship ...
                if maxShip.disjoint(allLand):
                    continue

                # Skip land that is wholly contained within the ship (i.e., the
                # ship has already sailed around/past this piece of land) ...
                if ship.contains(allLand):
                    continue

                # Append land to list ...
                relevantLands.append(allLand)

        # **********************************************************************

        # Deduce temporary file name and skip if it exists already ...
        tname = f"{output3}/ship/istep={istep:06d}.wkb.gz"
        if os.path.exists(tname):
            # Load [Multi]Polygon ...
            with gzip.open(tname, "rb") as fObj:
                ship = shapely.wkb.loads(fObj.read())
        else:
            # Check what type the ship is currently ...
            if isinstance(ship, shapely.geometry.point.Point):
                # Create copy of the ship ...
                limit = shapely.geometry.point.Point(lon, lat)
            else:
                # Extract the current limit of sailing (on water) ...
                limit = []
                for poly in pyguymer3.geo.extract_polys(ship):
                    limit += pyguymer3.geo.extract_lines(
                        removeLands(poly.exterior, relevantLands, simp = -1.0)
                    )
                limit = shapely.geometry.multilinestring.MultiLineString(limit)

                # Save [Multi]LineString ...
                with gzip.open(f"{output3}/limit/istep={istep:06d}.wkb.gz", "wb", compresslevel = 9) as fObj:
                    fObj.write(shapely.wkb.dumps(limit))

            # ******************************************************************

            # Find out how many points describe this [Multi]LineString ...
            nline = 0                                                           # [#]
            npoint = 0                                                          # [#]
            for line in pyguymer3.geo.extract_lines(limit):
                nline += 1                                                      # [#]
                npoint += len(line.coords)                                      # [#]

            print(f" > \"limit\" is described by {npoint:,d} Points in {nline:,d} LineStrings.")
            print(f"   The x-bound is {limit.bounds[0]:+011.6f}° ≤ longitude ≤ {limit.bounds[2]:+011.6f}°.")
            print(f"   The y-bound is {limit.bounds[1]:+010.6f}° ≤ latitude ≤ {limit.bounds[3]:+010.6f}°.")

            # ******************************************************************

            # Start timer ...
            start = time.time()                                                 # [s]

            # Check if this step is simplifying ...
            if (istep + 1) % freqSimp == 0:
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
                ship = removeLands(ship, relevantLands, simp = simp)
                ship = removeInteriorRings(ship)

                print(f" > filled/buffered/simplified/unioned/removed in {time.time() - start:,.2f} seconds.")
            else:
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
                ship = removeLands(ship, relevantLands, simp = -1.0)
                ship = removeInteriorRings(ship)

                print(f" > filled/buffered/filled/unioned/removed in {time.time() - start:,.2f} seconds.")

            # Clean up ...
            del limit

            # Save [Multi]Polygon ...
            with gzip.open(tname, "wb", compresslevel = 9) as fObj:
                fObj.write(shapely.wkb.dumps(ship))

        # **********************************************************************

        # Find out how many points describe this [Multi]Polygon ...
        npoint = 0                                                              # [#]
        npoly = 0                                                               # [#]
        for poly in pyguymer3.geo.extract_polys(ship):
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
            ax.add_geometries(
                pyguymer3.geo.extract_polys(ship),
                cartopy.crs.PlateCarree(),
                edgecolor = f"C{((istep + 1) // freqPlot) - 1:d}",
                facecolor = "none",
                linewidth = 1.0,
            )

    # **************************************************************************

    # Check if the user wants to make a plot ...
    if plot:
        # Determine output PNG file name ...
        png = f"{output3}/dur={dur:.2f}_local={repr(local)[0]}_freqPlot={freqPlot:d}_spd={spd:.1f}.png"

        print(f"Making \"{png}\" ...")

        # Configure figure ...
        fg.tight_layout()

        # Save figure ...
        fg.savefig(
            png,
                   dpi = 300,
            pad_inches = 0.1,
        )
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimize_image(png, strip = True)
