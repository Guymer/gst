#!/usr/bin/env python3

# Define function ...
def sail(
    lon,
    lat,
    spd,
    /,
    *,
           cons = 2.0,
          debug = __debug__,
            dur = 1.0,
     ffmpegPath = None,
    ffprobePath = None,
       freqLand = 100,
       freqPlot = 25,
       freqSimp = 25,
          local = False,
           nAng = 9,
          nIter = 100,
           plot = False,
           prec = 10000.0,
            res = "c",
        timeout = 60.0,
            tol = 1.0e-10,
):
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
    debug : bool, optional
        print debug messages
    dur : float, optional
        the duration of the voyage (in days)
    ffmpegPath : str, optional
        the path to the "ffmpeg" binary (if not provided then Python will
        attempt to find the binary itself)
    ffprobePath : str, optional
        the path to the "ffprobe" binary (if not provided then Python will
        attempt to find the binary itself)
    freqLand : int, optional
        re-evaluate the relevant land every freqLand iteration
    freqPlot : int, optional
        plot sailing contours every freqPlot iteration
    freqSimp : int, optional
        simplify the sailing contour every freqSimp iteration
    local : bool, optional
        the plot has only local extent
    nAng : int, optional
        the number of directions from each point that the vessel could sail in
    nIter : int, optional
        the maximum number of iterations (particularly the Vincenty formula)
    plot : bool, optional
        make a plot
    prec : float, optional
        the precision of the calculation (in metres)
    res : string, optional
        the resolution of the Global Self-Consistent Hierarchical
        High-Resolution Geography datasets
    timeout : float, optional
        the timeout for any requests/subprocess calls
    tol : float, optional
        the Euclidean distance that defines two points as being the same (in
        degrees)
    """

    # Import standard modules ...
    import datetime
    import gzip
    import os
    import shutil
    import time

    # Import special modules ...
    try:
        import cartopy
        cartopy.config.update(
            {
                "cache_dir" : os.path.expanduser("~/.local/share/cartopy_cache"),
            }
        )
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                       "backend" : "Agg",                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
                    "figure.dpi" : 300,
                "figure.figsize" : (9.6, 7.2),                                  # NOTE: See https://github.com/Guymer/misc/blob/main/README.md#matplotlib-figure-sizes
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
        import pyguymer3.media
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # Import sub-functions ...
    from .removeInteriorRingsWhichAreLand import removeInteriorRingsWhichAreLand
    from .removeLands import removeLands
    from .saveAllCanals import saveAllCanals
    from .saveAllLands import saveAllLands
    from .saveRelevantLands import saveRelevantLands

    # **************************************************************************

    # Try to find the paths if the user did not provide them ...
    if ffmpegPath is None:
        ffmpegPath = shutil.which("ffmpeg")
    if ffprobePath is None:
        ffprobePath = shutil.which("ffprobe")
    assert ffmpegPath is not None, "\"ffmpeg\" is not installed"
    assert ffprobePath is not None, "\"ffprobe\" is not installed"

    # **************************************************************************

    print(f"{spd:,.1f} knots is {0.001 * 1852.0 * spd:,.2f} kilometres/hour.")
    print(f"{spd:,.1f} knots is {0.001 * 24.0 * 1852.0 * spd:,.2f} kilometres/day.")

    # Determine how many degrees a [Multi]Polygon can be filled by ...
    fill = prec / pyguymer3.RESOLUTION_OF_EARTH                                 # [°]

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
        nIter = nIter,
    )                                                                           # [m], [°], [°]
    toSouthPole, _, _ = pyguymer3.geo.calc_dist_between_two_locs(
        lon,
        lat,
        lon,
        -90.0,
        nIter = nIter,
    )                                                                           # [m], [°], [°]

    print(f"The North Pole is {0.001 * toNorthPole:,.2f} kilometres up (ignoring all land).")
    print(f"The South Pole is {0.001 * toSouthPole:,.2f} kilometres down (ignoring all land).")

    # Create the initial starting Point ...
    ship = shapely.geometry.point.Point(lon, lat)

    # Calculate the maximum possible sailing distance (ignoring all land) ...
    # NOTE: If the distance is very large then the ship can sail anywhere.
    maxDist = (1852.0 * spd) * (24.0 * dur)                                     # [m]
    if maxDist > 0.5 * pyguymer3.CIRCUMFERENCE_OF_EARTH:
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
                debug = debug,
            fillSpace = "EuclideanSpace",
                nIter = nIter,
                  tol = tol,
        )
    else:
        maxShip = pyguymer3.geo.buffer(
            ship,
            maxDist,
                    debug = debug,
                     fill = +1.0,
                fillSpace = "EuclideanSpace",
            keepInteriors = False,
                     nAng = 361,
                    nIter = nIter,
                     simp = -1.0,
                      tol = tol,
        )

    # Check if the user is being far too coarse ...
    if prec > maxDist:
        raise Exception(f"the maximum possible sailing distance is {0.001 * maxDist:,.2f} kilometres but the precision is {0.001 * prec:,.2f} kilometres") from None

    print(f"The maximum possible sailing distance is {0.001 * maxDist:,.2f} kilometres (ignoring all land).")

    # Figure out how many steps are going to be required ...
    nstep = round(maxDist / prec)                                               # [#]

    # Find how long an iteration will cover ...
    # NOTE: Rounding to the nearest second ensures that the string will be
    #       pretty.
    sailDur = prec / (1852.0 * spd)                                             # [hr]
    sailDur = 3600.0 * sailDur                                                  # [s]
    sailDur = datetime.timedelta(seconds = round(sailDur))

    print(f"Each sailing iteration is {str(sailDur)} for the vessel.")

    # **************************************************************************

    # Determine first output folder name and make it if it is missing ...
    output1 = f"res={res}_cons={cons:.2e}_tol={tol:.2e}"
    if not os.path.exists(output1):
        os.mkdir(output1)
    if not os.path.exists(f"{output1}/allLands"):
        os.mkdir(f"{output1}/allLands")

    # Determine second output folder name and make it if it is missing ...
    if local:
        output2 = f"{output1}/local={repr(local)[0]}_nAng={nAng:d}_prec={prec:.2e}_lon={lon:+011.6f}_lat={lat:+010.6f}_dur={dur:.2f}_spd={spd:.1f}"
    else:
        output2 = f"{output1}/local={repr(local)[0]}_nAng={nAng:d}_prec={prec:.2e}"
    if not os.path.exists(output2):
        os.mkdir(output2)
    if not os.path.exists(f"{output2}/allLands"):
        os.mkdir(f"{output2}/allLands")

    # Determine third output folder name and make it if it is missing ...
    if local:
        output3 = f"{output2}/freqLand={freqLand:d}_freqSimp={freqSimp:d}"
    else:
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
        print(f"Making \"{allLandsName}\" ...")

        # Make the compressed WKB file of all of the land ...
        # NOTE: This is an un-buffered dataset without canals that is used
        #       purely for visualisation by other scripts.
        savedAllLands = saveAllLands(
            allLandsName,
            f"{output1}/allLands",
            allCanals = None,
                debug = debug,
                 dist = -1.0,
                 fill = 1.0,
            fillSpace = "EuclideanSpace",
               levels = (1, 5, 6),
                local = False,
              maxShip = None,
                 nAng = nAng,
                nIter = nIter,
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
            debug = debug,
             simp = simp,
              tol = tol,
        )
    else:
        # Set flag (if the file exists then canals must have been saved) ...
        savedAllCanals = True

    # Load all the canals ...
    # NOTE: Given how "allCanals" was made, we know that there aren't any
    #       invalid LineStrings, so don't bother checking for them.
    if savedAllCanals:
        with gzip.open(allCanalsName, mode = "rb") as gzObj:
            allCanals = pyguymer3.geo.extract_lines(
                shapely.wkb.loads(gzObj.read()),
                onlyValid = False,
            )
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
                debug = debug,
                 dist = prec,
                 fill = fill,
            fillSpace = "EuclideanSpace",
               levels = (1, 5, 6),
                local = local,
              maxShip = pyguymer3.geo.buffer(
                maxShip,
                prec,
                        debug = debug,
                         fill = +1.0,
                    fillSpace = "EuclideanSpace",
                keepInteriors = True,
                         nAng = 361,
                        nIter = nIter,
                         simp = -1.0,
                          tol = tol,
            ),
                 nAng = nAng,
                nIter = nIter,
                  res = res,
                 simp = simp,
                  tol = tol,
        )
    else:
        # Set flag (if the file exists then land must have been saved) ...
        savedAllLands = True

    # Load all the land ...
    # NOTE: Given how "allLands" was made, we know that there aren't any invalid
    #       Polygons, so don't bother checking for them.
    if savedAllLands:
        with gzip.open(allLandsName, mode = "rb") as gzObj:
            allLands = pyguymer3.geo.extract_polys(
                shapely.wkb.loads(gzObj.read()),
                onlyValid = False,
                   repair = False,
            )
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
        # Initialize list of animation frames ...
        pngOnes = []

        # Determine PNG "all map" file name as well as the MP4/WEBP animation
        # file names ...
        if local:
            pngAll = f"{output3}/freqPlot={freqPlot:d}.png"
            mp4Ones = f"{output3}/freqPlot={freqPlot:d}.mp4"
            webpOnes = f"{output3}/freqPlot={freqPlot:d}.webp"
        else:
            pngAll = f"{output3}/dur={dur:.2f}_freqPlot={freqPlot:d}_spd={spd:.1f}.png"
            mp4Ones = f"{output3}/dur={dur:.2f}_freqPlot={freqPlot:d}_spd={spd:.1f}.mp4"
            webpOnes = f"{output3}/dur={dur:.2f}_freqPlot={freqPlot:d}_spd={spd:.1f}.webp"

        # Check if the PNG "all map" needs making as well as the MP4/WEBP
        # animations ...
        pngAllExists = os.path.exists(pngAll)
        mp4OnesExists = os.path.exists(mp4Ones)
        webpOnesExists = os.path.exists(webpOnes)

        # Check if the PNG "all map" needs making ...
        if not pngAllExists:
            # Check if the user wants a local plot (for local people) ...
            if local:
                # Create figure ...
                fgAll = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

                # Create axis ...
                axAll = pyguymer3.geo.add_axis(
                    fgAll,
                      add_coastlines = False,
                       add_gridlines = True,
                               debug = debug,
                                dist = maxDist,
                                 lat = lat,
                                 lon = lon,
                               nIter = nIter,
                           onlyValid = False,
                              repair = False,
                    satellite_height = False,
                )

                # Configure axis ...
                pyguymer3.geo.add_GSHHG_map_underlay(
                    axAll,
                         debug = debug,
                     linewidth = 1.0,
                     onlyValid = False,
                        repair = False,
                    resolution = res,
                )
            else:
                # Create figure ...
                fgAll = matplotlib.pyplot.figure(figsize = (12.8, 7.2))

                # Create axis ...
                axAll = pyguymer3.geo.add_axis(
                    fgAll,
                    add_coastlines = False,
                     add_gridlines = True,
                             debug = debug,
                             nIter = nIter,
                         onlyValid = False,
                            repair = False,
                )

                # Configure axis ...
                pyguymer3.geo.add_map_background(
                    axAll,
                         debug = debug,
                    resolution = "large8192px",
                )

            # Plot Polygons ...
            axAll.add_geometries(
                allLands,
                cartopy.crs.PlateCarree(),
                edgecolor = (1.0, 0.0, 0.0, 0.2),
                facecolor = (1.0, 0.0, 0.0, 0.2),
                linewidth = 1.0,
                   zorder = 2.0,
            )

            # Plot Polygons ...
            # NOTE: Given how "maxShip" was made, we know that there aren't any
            #       invalid Polygons, so don't bother checking for them.
            axAll.add_geometries(
                pyguymer3.geo.extract_polys(
                    maxShip,
                    onlyValid = False,
                       repair = False,
                ),
                cartopy.crs.PlateCarree(),
                edgecolor = (0.0, 0.0, 0.0, 0.2),
                facecolor = (0.0, 0.0, 0.0, 0.2),
                linewidth = 1.0,
                   zorder = 2.1,
            )

    # **************************************************************************

    # Initialize area ...
    oldArea = 0.0                                                               # [°2]

    # Loop over iterations ...
    for istep in range(nstep):
        print(f"Iteration {istep + 1:,d}/{nstep:,d} ({0.001 * (istep + 1) * prec:,.2f} kilometres/{(istep + 1) * prec / (24.0 * 1852.0 * spd):,.4f} days of sailing) ...")

        # Check if the user wants to make a plot and that this iteration is one
        # of the ones to be plotted ...
        if plot and (istep + 1) % freqPlot == 0:
            # Determine PNG "one map" file name and append to list ...
            pngOne = f"{output3}/ship/istep={istep:06d}.png"
            pngOnes.append(pngOne)                                              # pylint: disable=E0606

            # Check if the PNG "one map" needs making ...
            pngOneExists = os.path.exists(pngOne)

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
                        debug = debug,
                         fill = +1.0,
                    fillSpace = "EuclideanSpace",
                         nAng = 361,
                        nIter = nIter,
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
                    relevantLands = pyguymer3.geo.extract_polys(
                        shapely.wkb.loads(gzObj.read()),
                        onlyValid = False,
                           repair = False,
                    )
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
                for poly in pyguymer3.geo.extract_polys(
                    ship,
                    onlyValid = False,
                       repair = False,
                ):
                    limit += pyguymer3.geo.extract_lines(
                        removeLands(
                            poly.exterior,
                            relevantLands,                                      # pylint: disable=E0606
                            debug = debug,
                             simp = -1.0,
                        ),
                        onlyValid = False,
                    )
                    for interior in poly.interiors:
                        limit += pyguymer3.geo.extract_lines(
                            removeLands(
                                interior,
                                relevantLands,
                                debug = debug,
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
            for line in pyguymer3.geo.extract_lines(
                limit,
                onlyValid = False,
            ):
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
                            debug = debug,
                             fill = fill,
                        fillSpace = "EuclideanSpace",
                    keepInteriors = True,
                             nAng = nAng,
                            nIter = nIter,
                             simp = simp,
                              tol = tol,
                )
                ship = shapely.ops.unary_union([limit, ship])
                ship = removeLands(
                    ship,
                    relevantLands,
                    debug = debug,
                     simp = simp,
                )
                ship = removeInteriorRingsWhichAreLand(
                    ship,
                    relevantLands,
                    onlyValid = False,
                        nIter = nIter,
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
                            debug = debug,
                             fill = fill,
                        fillSpace = "EuclideanSpace",
                    keepInteriors = False,
                             nAng = nAng,
                            nIter = nIter,
                             simp = -1.0,
                              tol = tol,
                )
                ship = shapely.ops.unary_union([limit, ship])
                ship = removeLands(
                    ship,
                    relevantLands,
                    debug = debug,
                     simp = -1.0,
                )
                ship = removeInteriorRingsWhichAreLand(
                    ship,
                    relevantLands,
                    onlyValid = False,
                        nIter = nIter,
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
        for poly in pyguymer3.geo.extract_polys(
            ship,
            onlyValid = False,
               repair = False,
        ):
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

            # Check if the PNG "all map" needs making ...
            if not pngAllExists:
                # Plot Polygons ...
                # NOTE: Given how "ship" was made, we know that there aren't any
                #       invalid Polygons, so don't bother checking for them.
                axAll.add_geometries(
                    pyguymer3.geo.extract_polys(
                        ship,
                        onlyValid = False,
                           repair = False,
                    ),
                    cartopy.crs.PlateCarree(),
                    edgecolor = f"C{((istep + 1) // freqPlot) - 1:d}",
                    facecolor = "none",
                    linewidth = 1.0,
                       zorder = 2.2,
                )

            # Check if the PNG "one map" needs making ...
            if not pngOneExists:
                # Check if the user wants a local plot (for local people) ...
                if local:
                    # Create figure ...
                    fgOne = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

                    # Create axis ...
                    axOne = pyguymer3.geo.add_axis(
                        fgOne,
                          add_coastlines = False,
                           add_gridlines = True,
                                   debug = debug,
                                    dist = maxDist,
                                     lat = lat,
                                     lon = lon,
                                   nIter = nIter,
                               onlyValid = False,
                                  repair = False,
                        satellite_height = False,
                    )

                    # Configure axis ...
                    pyguymer3.geo.add_GSHHG_map_underlay(
                        axOne,
                             debug = debug,
                         linewidth = 1.0,
                         onlyValid = False,
                            repair = False,
                        resolution = res,
                    )
                else:
                    # Create figure ...
                    fgOne = matplotlib.pyplot.figure(figsize = (12.8, 7.2))

                    # Create axis ...
                    axOne = pyguymer3.geo.add_axis(
                        fgOne,
                        add_coastlines = False,
                         add_gridlines = True,
                                 debug = debug,
                                 nIter = nIter,
                             onlyValid = False,
                                repair = False,
                    )

                    # Configure axis ...
                    pyguymer3.geo.add_map_background(
                        axOne,
                             debug = debug,
                        resolution = "large8192px",
                    )

                # Plot Polygons ...
                axOne.add_geometries(
                    allLands,
                    cartopy.crs.PlateCarree(),
                    edgecolor = (1.0, 0.0, 0.0, 1.0),
                    facecolor = (1.0, 0.0, 0.0, 0.2),
                    linewidth = 1.0,
                       zorder = 2.0,
                )

                # Plot Polygons ...
                # NOTE: Given how "maxShip" was made, we know that there aren't
                #       any invalid Polygons, so don't bother checking for them.
                axOne.add_geometries(
                    pyguymer3.geo.extract_polys(
                        maxShip,
                        onlyValid = False,
                           repair = False,
                    ),
                    cartopy.crs.PlateCarree(),
                    edgecolor = (0.0, 0.0, 0.0, 1.0),
                    facecolor = (0.0, 0.0, 0.0, 0.2),
                    linewidth = 1.0,
                       zorder = 2.1,
                )

                # Plot Polygons ...
                # NOTE: Given how "ship" was made, we know that there aren't any
                #       invalid Polygons, so don't bother checking for them.
                axOne.add_geometries(
                    pyguymer3.geo.extract_polys(
                        ship,
                        onlyValid = False,
                           repair = False,
                    ),
                    cartopy.crs.PlateCarree(),
                    edgecolor = "blue",
                    facecolor = "none",
                    linewidth = 1.0,
                       zorder = 2.2,
                )

                print(f"Making \"{pngOne}\" ...")

                # Configure figure ...
                fgOne.tight_layout()

                # Save figure ...
                fgOne.savefig(pngOne)
                matplotlib.pyplot.close(fgOne)

                # Optimize PNG ...
                pyguymer3.image.optimise_image(
                    pngOne,
                      debug = debug,
                      strip = True,
                    timeout = timeout,
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
        # Check if the PNG "all map" needs making ...
        if not pngAllExists:
            print(f"Making \"{pngAll}\" ...")

            # Configure figure ...
            fgAll.tight_layout()

            # Save figure ...
            fgAll.savefig(pngAll)
            matplotlib.pyplot.close(fgAll)

            # Optimize PNG ...
            pyguymer3.image.optimise_image(
                pngAll,
                  debug = debug,
                  strip = True,
                timeout = timeout,
            )

        # **********************************************************************

        # Check if the MP4 animation needs making ...
        if not mp4OnesExists:
            print(f"Making \"{mp4Ones}\" ...")

            # Save 25fps MP4 ...
            tmpName = pyguymer3.media.images2mp4(
                pngOnes,
                      debug = debug,
                 ffmpegPath = ffmpegPath,
                ffprobePath = ffprobePath,
                    timeout = None,
            )
            shutil.move(tmpName, mp4Ones)

        # **********************************************************************

        # Check if the WEBP animation needs making ...
        if not webpOnesExists:
            print(f"Making \"{webpOnes}\" ...")

            # Save 25fps WEBP ...
            pyguymer3.media.images2webp(
                pngOnes,
                webpOnes,
            )
