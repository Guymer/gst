#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import gzip
    import os
    import pathlib
    import subprocess
    import sysconfig

    # Import special modules ...
    try:
        import cartopy
        cartopy.config.update(
            {
                "cache_dir" : pathlib.PosixPath("~/.local/share/cartopy_cache").expanduser(),
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

    # **************************************************************************

    # Create argument parser and parse the arguments ...
    parser = argparse.ArgumentParser(
           allow_abbrev = False,
            description = "Show how narrow passages may be blocked.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action = "store_true",
          dest = "debug",
          help = "print debug messages",
    )
    parser.add_argument(
        "--dry-run",
        action = "store_true",
          dest = "dryRun",
          help = "don't run GST - just assume that all the required GST output is there already",
    )
    parser.add_argument(
        "--timeout",
        default = 60.0,
           help = "the timeout for any requests/subprocess calls (in seconds)",
           type = float,
    )
    args = parser.parse_args()

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
        for nAng, prec, color in combs:
            # Create short-hands ...
            # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
            freqLand = 24 * 40000 // prec                                       # [#]
            freqSimp = 40000 // prec                                            # [#]

            # Populate GST command ...
            cmd = [
                f"python{sysconfig.get_python_version()}", "-m", "gst",
                "0.0", "0.0", "20.0",           # dummy values
                "--duration", "0.01",           # dummy value
                "--freqLand", f"{freqLand:d}",  # ~daily land re-evaluation
                "--freqSimp", f"{freqSimp:d}",  # ~hourly simplification
                "--nAng", f"{nAng:d}",          # LOOP VARIABLE
                "--precision", f"{prec:.1f}",   # LOOP VARIABLE
                "--resolution", res,            # LOOP VARIABLE
            ]
            if args.debug:
                cmd.append("--debug")

            print(f'Running "{" ".join(cmd)}" ...')

            # Run GST ...
            if not args.dryRun:
                subprocess.run(
                    cmd,
                       check = False,
                    encoding = "utf-8",
                      stderr = subprocess.DEVNULL,
                      stdout = subprocess.DEVNULL,
                     timeout = None,
                )

        # **********************************************************************

        # Deduce PNG name, append it to the list and skip if it already exists ...
        frame = f"showNarrowPassages_res={res}.png"
        frames.append(frame)
        if os.path.exists(frame):
            continue

        print(f"Making \"{frame}\" ...")

        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

        # Initialize lists ...
        ax = []
        ext = []

        # Loop over locations ...
        for iloc, loc in enumerate(locs):
            print(f" > Making axis for \"lon={loc[0]:+.2f}°, lat={loc[1]:+.2f}°\" ...")

            # Create axis ...
            ax.append(
                pyguymer3.geo.add_axis(
                    fg,
                    coastlines_edgecolor = "white",
                    coastlines_linewidth = 1.0,
                                   debug = args.debug,
                                    dist = 100.0e3,
                                   index = iloc + 1,
                                     lat = loc[1],
                                     lon = loc[0],
                                   ncols = 3,
                                   nrows = 3,
                )
            )

            # Configure axis ...
            pyguymer3.geo.add_map_background(
                ax[iloc],
                     debug = args.debug,
                      name = "shaded-relief",
                resolution = "large8192px",
            )

            # Loop over combinations ...
            for nAng, prec, color in combs:
                # Deduce file name and skip if it is missing ...
                dname = f"res={res}_cons=2.00e+00_tol=1.00e-10/local=F_nAng={nAng:d}_prec={prec:.2e}"
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

            # Plot the central location ...
            # NOTE: As of 5/Dec/2023, the default "zorder" of the coastlines is
            #       1.5, the default "zorder" of the gridlines is 2.0 and the
            #       default "zorder" of the scattered points is 1.0.
            ax[iloc].scatter(
                [loc[0]],
                [loc[1]],
                    color = "gold",
                   marker = "*",
                transform = cartopy.crs.Geodetic(),
                   zorder = 5.0,
            )

            # Configure axis ...
            ax[iloc].set_title(f"lon={loc[0]:+.2f}°, lat={loc[1]:+.2f}°")

        # Configure figure ...
        fg.suptitle(f"res={res}")
        fg.tight_layout()

        # Save figure ...
        fg.savefig(frame)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimise_image(
            frame,
              debug = args.debug,
              strip = True,
            timeout = args.timeout,
        )

    # **************************************************************************

    print("Making \"showNarrowPassages.webp\" ...")

    # Save 1fps WEBP ...
    pyguymer3.media.images2webp(
        frames,
        "showNarrowPassages.webp",
        fps = 1.0,
    )

    # Set maximum sizes ...
    # NOTE: By inspection, the PNG frames are 2,160 px tall/wide.
    maxSizes = [512, 1024, 2048]                                                # [px]

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
        )
