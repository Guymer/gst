def sail(lon, lat, spd, kwArgCheck = None, detailed = False, dur = 1.0, freqFillSimp = 25, freqLand = 100, freqPlot = 50, local = False, nang = 10, plot = False, prec = 100.0, res = "110m", tol = 1.0e-10):
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
    detailed : bool, optional
            take account of minor islands
    dur : float, optional
            the duration of the voyage (in days)
    freqFillSimp : int, optional
            fill in and simplify the sailing contour every freqFillSimp iteration
    freqLand : int, optional
            re-evaluate the relevant land every freqLand iteration
    freqPlot : int, optional
            plot sailing contours every freqPlot iteration
    local : bool, optional
            the plot has only local extent
    nang : int, optional
            the number of directions from each point that the vessel could sail in
    plot : bool, optional
            make a plot
    prec : float, optional
            the precision of the calculation (in metres)
    res : string, optional
            the resolution of the Natural Earth datasets
    tol : float, optional
            the Euclidean distance that defines two points as being the same (in degrees)
    """

    # Improt standard modules ...
    import copy
    import gzip
    import math
    import os

    # Import special modules ...
    try:
        import cartopy
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import matplotlib
        matplotlib.use("Agg")                                                   # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
        import matplotlib.pyplot
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
    from .remove_interior_rings import remove_interior_rings
    from .remove_lands import remove_lands
    from .save_allLands import save_allLands

    # Check keyword arguments ...
    if kwArgCheck is not None:
        print(f"WARNING: \"{__name__}\" has been called with an extra positional argument")

    # **************************************************************************

    # Determine how many degrees (of longitude) a [Multi]Polygon can be
    # simplified by at the point where a degree (of longitude) is the largest,
    # i.e., the equator ...
    # NOTE: See https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
    radiusOfEarth = 6371008.8                                                   # [m]
    circumOfEarth = 2.0 * math.pi * radiusOfEarth                               # [m]
    resoluOfEarth = circumOfEarth / 360.0                                       # [m/°]
    simp = prec / resoluOfEarth                                                 # [°]

    # Add conservatism ...
    simp *= 0.1                                                                 # [°]

    # Create the initial starting Point ...
    ship = shapely.geometry.point.Point(lon, lat)

    # Calculate the maximum possible sailing distance (ignoring all land) ...
    maxDist = (1852.0 * spd) * (24.0 * dur)                                     # [m]
    maxShip = pyguymer3.geo.buffer(ship, maxDist, debug = True, nang = nang, simp = simp, tol = tol)
    maxShipExt = [maxShip.bounds[0], maxShip.bounds[2], maxShip.bounds[1], maxShip.bounds[3]]   # [°], [°], [°], [°]

    # Determine the maximum symmetric sailing distance ...
    maxShipLon = max(abs(maxShipExt[0] - lon), abs(maxShipExt[1] - lon))        # [°]
    maxShipLat = max(abs(maxShipExt[2] - lat), abs(maxShipExt[3] - lat))        # [°]
    maxShipHyp = max(maxShipLon, maxShipLat)                                    # [°]
    maxShipExtSym = [lon - maxShipHyp, lon + maxShipHyp, lat - maxShipHyp, lat + maxShipHyp]    # [°], [°], [°], [°]

    # Check if the user is being far too coarse ...
    if prec > maxDist:
        raise Exception(f"the maximum possible sailing distance is {maxDist:,.1f}m but the precision is {prec:,.1f}m") from None

    print(f"The maximum possible sailing distance is {0.001 * maxDist:,.2f}km (ignoring all land).")

    # Figure out how many steps are going to be required ...
    nstep = round(maxDist / prec)                                               # [#]

    print(f"Each sailing iteration is {60.0 * 60.0 * prec / (1852.0 * spd):,.1f}s for the vessel.")

    # **************************************************************************

    # Determine first output folder name and make it if it is missing ...
    output1 = f"detailed={repr(detailed)[0]}_nang={nang:d}_prec={prec:.2e}_res={res}_simp={simp:.2e}_tol={tol:.2e}"
    if not os.path.exists(output1):
        os.mkdir(output1)

    # Determine second output folder name and make it if it is missing ...
    output2 = f"{output1}/allLands"
    if not os.path.exists(output2):
        os.mkdir(output2)

    # Determine third output folder name and make it if it is missing ...
    output3 = f"{output1}/freqFillSimp={freqFillSimp:d}_freqLand={freqLand:d}_lat={lat:+010.6f}_lon={lon:+011.6f}"
    if not os.path.exists(output3):
        os.mkdir(output3)

    # Determine fourth output folder name and make it if it is missing ...
    output4 = f"{output3}/contours"
    if not os.path.exists(output4):
        os.mkdir(output4)

    # **************************************************************************

    # Deduce input filename ...
    allLandsName = f"{output1}/allLands.wkb.gz"

    # Check if the input file is missing ...
    if not os.path.exists(allLandsName):
        print(f"Making \"{allLandsName}\" ...")

        # Make the compressed WKB file of all of the land ...
        save_allLands(allLandsName, output2, prec, debug = True, detailed = detailed, fill = -1.0, nang = nang, res = res, simp = simp, tol = tol)

    # Load all the land ...
    allLands = shapely.wkb.loads(gzip.open(allLandsName, "rb").read())

    # **************************************************************************

    # Check if the user wants to make a plot ...
    if plot:
        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = 300)
        if local:
            ax = matplotlib.pyplot.axes(projection = cartopy.crs.Orthographic(central_longitude = lon, central_latitude = lat))
            ax.set_extent(maxShipExt)
        else:
            ax = matplotlib.pyplot.axes(projection = cartopy.crs.Robinson())
            ax.set_global()
        pyguymer3.geo.add_map_background(ax, resolution = "large4096px")
        pyguymer3.geo.add_horizontal_gridlines(ax, maxShipExtSym, ngrid = 5)
        pyguymer3.geo.add_vertical_gridlines(ax, maxShipExtSym, ngrid = 5)

        # Plot Polygons ...
        ax.add_geometries(
            allLands,
            cartopy.crs.PlateCarree(),
            edgecolor = (0.0, 0.0, 0.0, 0.1),
            facecolor = (1.0, 0.0, 0.0, 0.1),
            linewidth = 1.0
        )

    # Loop over iterations ...
    for istep in range(nstep):
        # Check type ...
        if isinstance(ship, shapely.geometry.point.Point):
            print(f"Iteration {istep + 1:,d}/{nstep:,d} ({0.001 * (istep + 1) * prec:,.2f} km of sailing) ...")
        elif isinstance(ship, shapely.geometry.polygon.Polygon):
            print(f"Iteration {istep + 1:,d}/{nstep:,d} ({0.001 * (istep + 1) * prec:,.2f} km of sailing) ...")
        else:
            raise TypeError(f"\"ship\" is an unexpected type ({repr(type(ship))})") from None

        # **********************************************************************

        # Check if this step needs the list of relevant land updating ...
        if istep % freqLand == 0:
            print(" > Re-evaluating the relevant land ...")

            # Initialize list ...
            relevantLands = []

            # Loop over Polygons in the MultiPolygon of all of the land ...
            for allLand in allLands:
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
        tname = f"{output4}/istep={istep:06d}.wkb.gz"
        if os.path.exists(tname):
            # Load [Multi]Polygon ...
            ship = shapely.wkb.loads(gzip.open(tname, "rb").read())
        else:
            # Check what type the ship is currently ...
            if isinstance(ship, shapely.geometry.point.Point):
                # Create dummy variable ...
                limit = copy.copy(ship)
            else:
                # Extract the current limit of sailing (on water) ...
                limit = remove_lands(ship.exterior, relevantLands, simp = -1.0)

            # Check if this step filling/simplifying ...
            if (istep + 1) % freqFillSimp == 0:
                print(" > Filling in and simplifying ...")

                # Sail ...
                limit = pyguymer3.geo.buffer(limit, prec, fill = 10.0 * simp, nang = nang, simp = simp, tol = tol)
                ship = shapely.ops.unary_union([limit, ship])
                ship = remove_lands(ship, relevantLands, simp = simp)
                ship = remove_interior_rings(ship, tol = tol)
            else:
                # Sail ...
                limit = pyguymer3.geo.buffer(limit, prec, fill = -1.0, nang = nang, simp = -1.0, tol = tol)
                ship = shapely.ops.unary_union([limit, ship])
                ship = remove_lands(ship, relevantLands, simp = -1.0)
                ship = remove_interior_rings(ship, tol = tol)

            # Clean up ...
            del limit

            # Save [Multi]Polygon ...
            gzip.open(tname, "wb", compresslevel = 9).write(shapely.wkb.dumps(ship))

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
                linewidth = 1.0
            )

    # Check if the user wants to make a plot ...
    if plot:
        # Determine output PNG file name ...
        png = f"{output3}/dur={dur:.2f}_local={repr(local)[0]}_freqPlot={freqPlot:d}_spd={spd:.1f}.png"

        print(f"Making \"{png}\" ...")

        # Save figure ...
        fg.savefig(png, bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimize_image(png, strip = True)
