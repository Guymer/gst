#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.11/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import gzip
    import os
    import subprocess

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
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # **************************************************************************

    # Define combinations ...
    combs = [
        ( 9, 5000, (1.0, 0.0, 0.0, 0.5),),
        (17, 2500, (0.0, 1.0, 0.0, 0.5),),
        (33, 1250, (0.0, 0.0, 1.0, 0.5),),
    ]

    # Define locations ...
    locs = [
        ( 11.8,  55.5),                 # Zealand
        ( -5.6,  36.0),                 # Gibraltar
        (-79.7,   9.1),                 # Panama Canal
        ( 32.3,  30.6),                 # Suez Canal
        ( 43.4,  12.6),                 # Bab-el-Mandeb
        (-69.6, -52.5),                 # Primera Angostura
        ( 26.5,  40.2),                 # Dardanelles
        ( 29.1,  41.1),                 # Bosporus Strait
        (104.0,   0.9),                 # Singapore
    ]                                                                           # [°]

    # Define resolutions ...
    ress = [
        "c",                            # crude
        "l",                            # low
        "i",                            # intermediate
        "h",                            # high
        "f",                            # full
    ]

    # **************************************************************************

    # Initialize list ...
    frames = []

    # Loop over resolutions ...
    for res in ress:
        # Loop over combinations ...
        for nang, prec, color in combs:
            # Create short-hands ...
            # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
            freqLand = 24 * 40000 // prec                                       # [#]
            freqSimp = 40000 // prec                                            # [#]

            # Populate GST command ...
            cmd = [
                "python3.11", "run.py",
                "-1.0", "+50.5", "20.0",        # depart Portsmouth Harbour at 20 knots
                "--duration", "0.01",           # some sailing (20 knots * 0.01 days = 8.89 kilometres)
                "--freqLand", f"{freqLand:d}",  # ~daily land re-evaluation
                "--freqSimp", f"{freqSimp:d}",  # ~hourly simplification
                "--nang", f"{nang:d}",          # LOOP VARIABLE
                "--precision", f"{prec:.1f}",   # LOOP VARIABLE
                "--resolution", res,            # LOOP VARIABLE
            ]

            print(f'Running "{" ".join(cmd)}" ...')

            # Run GST ...
            subprocess.run(
                cmd,
                   check = False,
                encoding = "utf-8",
                  stderr = subprocess.DEVNULL,
                  stdout = subprocess.DEVNULL,
            )

        # **********************************************************************

        # Deduce PNG name, append it to the list and skip if it already exists ...
        frame = f"showNarrowPassages_res={res}.png"
        frames.append(frame)
        if os.path.exists(frame):
            continue

        print(f"Making \"{frame}\" ...")

        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (12, 12))

        # Initialize lists ...
        ax = []
        ext = []

        # Loop over locations ...
        for iloc, loc in enumerate(locs):
            print(f" > Making axis for \"lon={loc[0]:+.2f}°, lat={loc[1]:+.2f}°\" ...")

            # Create axis ...
            ax.append(
                fg.add_subplot(
                    3,
                    3,
                    iloc + 1,
                    projection = cartopy.crs.Orthographic(
                        central_longitude = loc[0],
                         central_latitude = loc[1],
                    )
                )
            )

            # Find how large a 100km radius circle is around the central
            # location ...
            point = shapely.geometry.point.Point(loc[0], loc[1])
            poly = pyguymer3.geo.buffer(
                point,
                100.0e3,
                fill = -1.0,
                nang = 9,
                simp = -1.0,
            )

            # Create extent ...
            ext.append(
                [
                    poly.bounds[0],     # minx
                    poly.bounds[2],     # maxx
                    poly.bounds[1],     # miny
                    poly.bounds[3],     # maxy
                ]
            )                                                                   # [°]

            # Clean up ...
            del point, poly

            # Configure axis ...
            ax[iloc].set_extent(ext[iloc])
            pyguymer3.geo.add_map_background(
                ax[iloc],
                      name = "shaded-relief",
                resolution = "large8192px",
            )
            pyguymer3.geo.add_horizontal_gridlines(
                ax[iloc],
                locs = range(-90, 91, 1),
            )
            pyguymer3.geo.add_vertical_gridlines(
                ax[iloc],
                locs = range(-180, 181, 1),
            )

            # Loop over combinations ...
            for nang, prec, color in combs:
                # Deduce file name and skip if it is missing ...
                dname = f"res={res}_cons=2.00e+00_tol=1.00e-10/nang={nang:d}_prec={prec:.2e}"
                fname = f"{dname}/allLands.wkb.gz"
                if not os.path.exists(fname):
                    continue

                print(f"   > Plotting \"{fname}\" ...")

                # Load [Multi]Polygon ...
                with gzip.open(fname, mode = "rb") as gzObj:
                    allLands = shapely.wkb.loads(gzObj.read())

                # Plot Polygons ...
                # NOTE: Given how "allLands" was made, we know that there aren't
                #       any invalid Polygons, so don't bother checking for them.
                ax[iloc].add_geometries(
                    pyguymer3.geo.extract_polys(allLands, onlyValid = False, repair = False),
                    cartopy.crs.PlateCarree(),
                    edgecolor = (0.0, 0.0, 0.0, 0.5),
                    facecolor = color,
                    linewidth = 1.0,
                )

                # Clean up ...
                del allLands

            # Plot the central location ...
            ax[iloc].scatter(
                [loc[0]],
                [loc[1]],
                    color = "gold",
                   marker = "*",
                transform = cartopy.crs.Geodetic(),
                   zorder = 5.0,
            )

            # Configure axis ...
            pyguymer3.geo.add_coastlines(
                ax[iloc],
                 colorName = "white",
                     level = 1,
                 linewidth = 1.0,
                resolution = "f",
            )
            pyguymer3.geo.add_coastlines(
                ax[iloc],
                 colorName = "white",
                     level = 5,
                 linewidth = 1.0,
                resolution = "f",
            )
            pyguymer3.geo.add_coastlines(
                ax[iloc],
                 colorName = "white",
                     level = 6,
                 linewidth = 1.0,
                resolution = "f",
            )
            ax[iloc].set_title(f"lon={loc[0]:+.2f}°, lat={loc[1]:+.2f}°")

        # Configure figure ...
        fg.suptitle(f"res={res}")
        fg.tight_layout()

        # Save figure ...
        fg.savefig(frame)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimize_image(frame, strip = True)

    # **************************************************************************

    print("Making \"showNarrowPassages.webp\" ...")

    # Save 1fps WEBP ...
    pyguymer3.media.images2webp(
        frames,
        "showNarrowPassages.webp",
          fps = 1.0,
        strip = True,
    )

    # Set maximum sizes ...
    # NOTE: By inspection, the PNG frames are 3600px tall/wide.
    maxSizes = [256, 512, 1024, 2048]                                           # [px]

    # Loop over maximum sizes ...
    for maxSize in maxSizes:
        print(f"Making \"showNarrowPassages{maxSize:04d}px.webp\" ...")

        # Save 1fps WEBP ...
        pyguymer3.media.images2webp(
            frames,
            f"showNarrowPassages{maxSize:04d}px.webp",
                     fps = 1.0,
            screenHeight = maxSize,
             screenWidth = maxSize,
                   strip = True,
        )
