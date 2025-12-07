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
                "cache_dir" : pathlib.PosixPath("~/.local/share/cartopy").expanduser(),
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
        import numpy
    except:
        raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
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
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # **************************************************************************

    # Create argument parser and parse the arguments ...
    parser = argparse.ArgumentParser(
           allow_abbrev = False,
            description = "Compare pyguymer3.geo.buffer() angular resolutions.",
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
        "--plot",
        action = "store_true",
          help = "make maps and animation",
    )
    parser.add_argument(
        "--timeout",
        default = 60.0,
           help = "the timeout for any requests/subprocess calls (in seconds)",
           type = float,
    )
    args = parser.parse_args()

    # **************************************************************************

    # Define resolution ...
    res = "i"

    # Define starting location ...
    lon = -1.0                                                                  # [°]
    lat = 50.5                                                                  # [°]

    # **************************************************************************

    # Loop over number of angles ...
    for nAng in [9, 17, 33, 65, 129, 257]:
        # Populate GST command ...
        cmd = [
            f"python{sysconfig.get_python_version()}", "-m", "gst",
            f"{lon:+.1f}", f"{lat:+.1f}", "20.0",
            "--duration", "0.09",       # some sailing (20 knots * 0.09 days = 80.01 kilometres)
            "--freqLand", "768",        # ~daily land re-evaluation
            "--freqPlot", "1",          # plot every 1.25 kilometres
            "--freqSimp", "768",        # ~daily simplification
            "--local",                  # save time by only considering local land
            "--nAng", f"{nAng:d}",      # LOOP VARIABLE
            "--precision", "1250.0",    # converged precision (from "compareBufferRadialResolutions.py")
            "--resolution", res,
        ]
        if args.debug:
            cmd.append("--debug")
        if args.plot:
            cmd.append("--plot")

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

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (12.8, 7.2))

    # Create axis ...
    # NOTE: Really, I should be plotting "allLands" to be consistent with the
    #       ships, however, as each ship (potentially) is using different
    #       collections of land then I will just use the raw GSHHG dataset
    #       instead.
    ax1 = pyguymer3.geo.add_axis(
        fg,
         coastlines_edgecolor = (1.0, 0.0, 0.0, 1.0),
         coastlines_facecolor = (1.0, 0.0, 0.0, 0.5),
         coastlines_linewidth = 1.0,
        coastlines_resolution = res,
                        debug = args.debug,
                         dist = 100.0e3,
                        index = 1,
                          lat = lat,
                          lon = lon,
                        ncols = 2,
                        nrows = 1,
    )

    # Create axis ...
    ax2 = fg.add_subplot(
        1,
        2,
        2,
    )

    # Configure axis ...
    pyguymer3.geo.add_map_background(
        ax1,
             debug = args.debug,
        resolution = "large8192px",
    )

    # **************************************************************************

    # Initialize dictionary and list ...
    data = {}
    labels = []
    lines = []

    # Loop over number of angles ...
    for iang, nAng in enumerate([9, 17, 33, 65, 129, 257]):
        # Create short-hand ...
        color = f"C{iang:d}"

        # Loop over distances ...
        for dist in range(10, 90, 10):
            # Determine the step count ...
            istep = ((1000 * dist) // 1250) - 1                                 # [#]

            # Deduce directory name ...
            dname = f"res={res}_cons=2.00e+00_tol=1.00e-10/local=T_nAng={nAng:d}_prec=1.25e+03_lon={lon:+011.6f}_lat={lat:+010.6f}_dur=0.09_spd=20.0/freqLand=768_freqSimp=768/ship"

            # Deduce file name and skip if it is missing ...
            fname = f"{dname}/istep={istep:06d}.wkb.gz"
            if not os.path.exists(fname):
                continue

            print(f"Plotting \"{fname}\" ...")

            # Load Polygon ...
            with gzip.open(fname, mode = "rb") as gzObj:
                ship = shapely.wkb.loads(gzObj.read())

            # Populate dictionary ...
            key = f"{dist:,d}"
            if key not in data:
                data[key] = {
                    "nAng" : [],                                                # [#]
                    "area" : [],                                                # [°2]
                }
            data[key]["nAng"].append(nAng)                                      # [#]
            data[key]["area"].append(ship.area)                                 # [°2]

            # Plot Polygon ...
            ax1.add_geometries(
                [ship],
                cartopy.crs.PlateCarree(),
                edgecolor = color,
                facecolor = "none",
                linewidth = 1.0,
            )

            # Check if it is the first distance for this number of angles ...
            label = f"{nAng:,d}"
            if label not in labels:
                # Add an entry to the legend ...
                labels.append(label)
                lines.append(matplotlib.lines.Line2D([], [], color = color))

    # Plot the starting location ...
    # NOTE: As of 5/Dec/2023, the default "zorder" of the coastlines is 1.5, the
    #       default "zorder" of the gridlines is 2.0 and the default "zorder" of
    #       the scattered points is 1.0.
    ax1.scatter(
        [lon],
        [lat],
            color = "gold",
           marker = "*",
        transform = cartopy.crs.Geodetic(),
           zorder = 5.0,
    )

    # **************************************************************************

    # Loop over distances ...
    for key in sorted(list(data.keys())):
        # Create short-hands ...
        nAng = numpy.array(data[key]["nAng"])                                   # [#]
        area = numpy.array(data[key]["area"])                                   # [°2]

        # Convert to ratio ...
        area /= area[-1]

        # Convert to percentage ...
        area *= 100.0                                                           # [%]

        # Plot data ...
        ax2.plot(
            nAng,
            area,
             label = key,
            marker = "d",
        )

    # **************************************************************************

    # Configure axis ...
    ax1.legend(
        lines,
        labels,
          loc = "upper center",
         ncol = 3,
        title = "Number Of Angles",
    )

    # Configure axis ...
    ax2.axhspan(
        99,
        101,
            alpha = 0.25,
        facecolor = "green",
    )
    ax2.grid()
    ax2.legend(
          loc = "lower right",
        title = "Distances [km]",
    )
    ax2.semilogx()
    ax2.set_xlabel("Number Of Angles")
    ax2.set_xticks(
        [8, 16, 32, 64, 128, 256],
        labels = ["8", "16", "32", "64", "128", "256"],
    )
    ax2.set_ylabel("Euclidean Area [%]")
    ax2.set_ylim(90, 102)
    ax2.set_yticks(range(90, 103))

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("compareBufferAngularResolutions.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimise_image(
        "compareBufferAngularResolutions.png",
          debug = args.debug,
          strip = True,
        timeout = args.timeout,
    )
