def sail(lon, lat, spd, debug = False, detailed = True, dur = 1.0, local = False, nang = 19, nth = 5, plot = True, prec = 10000.0, res = "110m"):
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
    debug : bool, optional
            print debug messages
    detailed : bool, optional
            take account of minor islands
    dur : float, optional
            the duration of the voyage (in days)
    local : bool, optional
            the plot has only local extent
    nang : int, optional
            the number of directions from each point that the vessel could sail in
    nth : int, optional
            plot sailing contours every nth iteration
    plot : bool, optional
            make a plot
    prec : float, optional
            the precision of the calculation (in metres)
    res : string, optional
            the resolution of the Natural Earth datasets
    """

    # Improt standard modules ...
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
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # Import sub-functions ...
    from .remove_interior_rings import remove_interior_rings
    from .remove_lands import remove_lands
    from .save_allLands import save_allLands

    # **************************************************************************

    # Determine how many degrees (of longitude) a [Multi]Polygon can be
    # simplified by at the points where a degree (of longitude) is the largest,
    # i.e., the equator ...
    # NOTE: See https://en.wikipedia.org/wiki/Earth_radius#Mean_radius
    radiusOfEarth = 6371008.8                                                   # [m]
    circumOfEarth = 2.0 * math.pi * radiusOfEarth                               # [m]
    resoluOfEarth = circumOfEarth / 360.0                                       # [m/°]
    simp = prec / resoluOfEarth                                                 # [°]

    # Create the initial starting Point ...
    ship = shapely.geometry.point.Point(lon, lat)

    # Calculate the maximum possible sailing distance (ignoring all land) ...
    maxDist = (1852.0 * spd) * (24.0 * dur)                                     # [m]
    maxShip = pyguymer3.buffer(ship, maxDist, debug = debug, nang = nang, simp = simp)

    # Figure out how many steps are going to be required ...
    nstep = round(maxDist / prec)                                               # [#]

    # **************************************************************************

    # Determine first output folder name and make it if it is missing ...
    output1 = f"detailed={repr(detailed)}_nang={repr(nang)}_res={res}_simp={repr(simp)}"
    if not os.path.exists(output1):
        os.mkdir(output1)

    # Determine second output folder name and make it if it is missing ...
    output2 = f"{output1}/lon={repr(lon)}_lat={repr(lat)}_spd={repr(spd)}_dur={repr(dur)}"
    if not os.path.exists(output2):
        os.mkdir(output2)

    # **************************************************************************

    # Deduce input filename ...
    allLandsName = f"{output1}/allLands.wkb.gz"

    # Check if the input file is missing ...
    if not os.path.exists(allLandsName):
        print(f"Making \"{allLandsName}\" ...")

        # Make the compressed WKB file of all of the land ...
        save_allLands(allLandsName, prec, debug = debug, detailed = detailed, nang = nang, res = res, simp = simp)

    # Load all the land ...
    allLands = shapely.wkb.loads(gzip.open(allLandsName, "rb").read())

    # **************************************************************************

    # Check if the user wants to make a plot ...
    if plot:
        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = 300)
        if local:
            ax = matplotlib.pyplot.axes(projection = cartopy.crs.Orthographic(central_longitude = lon, central_latitude = lat))
            ax.set_extent([maxShip.bounds[0], maxShip.bounds[2], maxShip.bounds[1], maxShip.bounds[3]])
        else:
            ax = matplotlib.pyplot.axes(projection = cartopy.crs.Robinson())
            ax.set_global()
        pyguymer3.add_map_background(ax, resolution = "large4096px")

    # Loop over iterations ...
    for istep in range(nstep):
        print(f"Iteration {istep + 1:,d}/{nstep:,d} ({0.001 * (istep + 1) * prec:,.2f} km of sailing) ...")

        # **********************************************************************

        # Check if this step needs the list of relevant land updating ...
        if istep % 100 == 0:
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

        # Sail ...
        # TODO: Can I save time by not buffering the points that lie on
        #       coastlines? See:
        #         * https://shapely.readthedocs.io/en/stable/manual.html#shared-paths
        #       Alternatively, are coastline points in the land or in the sea or
        #       in both? If they can be identified, then skip them.
        #       Alternatively, instead of removing land via difference(), remove
        #       individual points from the LinearRing that are on land and
        #       use a LineString instead.
        ship = pyguymer3.buffer(ship, prec, debug = debug, nang = nang, simp = simp)
        ship = remove_lands(ship, relevantLands, simp = simp)
        ship = remove_interior_rings(ship)

        # Check if the user wants to make a plot and that this iteration is one
        # of the ones to be plotted ...
        if plot and (istep + 1) % nth == 0:
            print("  Plotting ...")

            # Plot [Multi]Polygon ...
            ax.add_geometries([ship], cartopy.crs.PlateCarree(), alpha = 1.0, edgecolor = f"C{((istep + 1) // nth) - 1:d}", facecolor = "none", linewidth = 1.0)

    # Check if the user wants to make a plot ...
    if plot:
        # Determine output PNG file name ...
        png = f"{output2}/local={repr(local)}_nth={repr(nth)}.png"

        print(f"Making \"{png}\" ...")

        # Save figure ...
        fg.savefig(png, bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.optimize_image(png, strip = True)
