#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import os
    import pathlib

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
            description = "Compare GSHHG map resolutions.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action = "store_true",
          dest = "debug",
          help = "print debug messages",
    )
    parser.add_argument(
        "--timeout",
        default = 60.0,
           help = "the timeout for any requests/subprocess calls (in seconds)",
           type = float,
    )
    args = parser.parse_args()

    # ******************************************************************************

    # Define central location ...
    lon = -1.0                                                                  # [°]
    lat = 50.5                                                                  # [°]

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
        # Deduce PNG name, append it to the list and skip if it already exists ...
        frame = f"compareGshhgMapResolutions_res={res}.png"
        frames.append(frame)
        if os.path.exists(frame):
            continue

        print(f"Making \"{frame}\" ...")

        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

        # Create axis ...
        ax = pyguymer3.geo.add_axis(
            fg,
            add_coastlines = False,
                     debug = args.debug,
                      dist = 100.0e3,
                       lat = lat,
                       lon = lon,
        )

        # Configure axis ...
        pyguymer3.geo.add_map_background(
            ax,
                 debug = args.debug,
                  name = "shaded-relief",
            resolution = "large8192px",
        )

        # Deduce Shapefile name ...
        sfile = cartopy.io.shapereader.gshhs(
            level = 1,
            scale = res,
        )

        print(f" > Loading \"{sfile}\" ...")

        # Initialize list ...
        polys = []

        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Add the Polygons to the list ...
            polys += pyguymer3.geo.extract_polys(record.geometry, onlyValid = True, repair = True)

        # Plot Polygons ...
        ax.add_geometries(
            polys,
            cartopy.crs.PlateCarree(),
            edgecolor = (1.0, 0.0, 0.0, 1.0),
            facecolor = (1.0, 0.0, 0.0, 0.5),
            linewidth = 1.0,
        )

        # Plot the central location ...
        # NOTE: As of 5/Dec/2023, the default "zorder" of the coastlines is 1.5,
        #       the default "zorder" of the gridlines is 2.0 and the default
        #       "zorder" of the scattered points is 1.0.
        ax.scatter(
            [lon],
            [lat],
                color = "gold",
               marker = "*",
            transform = cartopy.crs.Geodetic(),
               zorder = 5.0,
        )

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

    print("Making \"compareGshhgMapResolutions.webp\" ...")

    # Save 1fps WEBP ...
    pyguymer3.media.images2webp(
        frames,
        "compareGshhgMapResolutions.webp",
        fps = 1.0,
    )

    # Set maximum sizes ...
    # NOTE: By inspection, the PNG frames are 2,160 px tall/wide.
    maxSizes = [512, 1024, 2048]                                                # [px]

    # Loop over maximum sizes ...
    for maxSize in maxSizes:
        print(f"Making \"compareGshhgMapResolutions{maxSize:04d}px.webp\" ...")

        # Save 1fps WEBP ...
        pyguymer3.media.images2webp(
            frames,
            f"compareGshhgMapResolutions{maxSize:04d}px.webp",
                     fps = 1.0,
            screenHeight = maxSize,
             screenWidth = maxSize,
        )
