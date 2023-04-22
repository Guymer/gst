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
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # Define starting location ...
    lon = -1.0                                                                  # [°]
    lat = 50.5                                                                  # [°]

    # **************************************************************************

    # Initialize global bounding box ...
    xmin = +180.0                                                               # [°]
    ymin =  +90.0                                                               # [°]
    xmax = -180.0                                                               # [°]
    ymax =  -90.0                                                               # [°]

    # Loop over number of angles ...
    for nang in [9, 17, 33, 65, 129, 257]:
        # Populate GST command ...
        cmd = [
            "python3.11", "run.py",
            f"{lon:+.1f}", f"{lat:+.1f}", "20.0",
            "--duration", "0.09",       # some sailing (20 knots * 0.09 days = 80.01 kilometres)
            "--freqLand", "768",        # ~daily land re-evaluation
            "--freqSimp", "768",        # ~daily simplification
            "--nang", f"{nang:d}",      # LOOP VARIABLE
            "--precision", "1250.0",    # converged precision (from "compareBufferRadialResolutions.py")
            "--resolution", "i",        # intermediate coastline resolution
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

        # Loop over distances ...
        for dist in range(10, 90, 10):
            # Determine the step count ...
            istep = ((1000 * dist) // 1250) - 1                                 # [#]

            # Deduce directory name ...
            dname = f"res=i_cons=2.00e+00_tol=1.00e-10/nang={nang:d}_prec=1.25e+03/freqLand=768_freqSimp=768_lon={lon:+011.6f}_lat={lat:+010.6f}/ship"

            # Deduce file name and skip if it is missing ...
            fname = f"{dname}/istep={istep:06d}.wkb.gz"
            if not os.path.exists(fname):
                continue

            print(f"Surveying \"{fname}\" ...")

            # Load Polygon ...
            with gzip.open(fname, mode = "rb") as gzObj:
                ship = shapely.wkb.loads(gzObj.read())

            # Update global bounding box ...
            xmin = min(xmin, ship.bounds[0])                                    # [°]
            ymin = min(ymin, ship.bounds[1])                                    # [°]
            xmax = max(xmax, ship.bounds[2])                                    # [°]
            ymax = max(ymax, ship.bounds[3])                                    # [°]

            # Clean up ...
            del ship

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (9, 12))

    # Create axis ...
    ax1 = pyguymer3.geo.add_top_down_axis(
        fg,
        lon,
        lat,
        90.0e3,
        nrows = 2,
        ncols = 1,
        index = 1,
    )

    # Create axis ...
    ax2 = fg.add_subplot(
        2,
        1,
        2,
    )

    # Configure axis ...
    # NOTE: Really, I should be plotting "allLands" to be consistent with the
    #       ships, however, as each ship (potentially) is using different
    #       collections of land then I will just use the raw GSHHG dataset
    #       instead.
    pyguymer3.geo.add_map_background(ax1, resolution = "large8192px")
    pyguymer3.geo.add_horizontal_gridlines(
        ax1,
        locs = [50.0, 50.5, 51.0],
    )
    pyguymer3.geo.add_vertical_gridlines(
        ax1,
        locs = [-2.0, -1.5, -1.0, -0.5, 0.0],
    )
    pyguymer3.geo.add_coastlines(
        ax1,
         colorName = "red",
          faceOpac = 0.5,
             level = 1,
         linewidth = 1.0,
        resolution = "i",
    )
    pyguymer3.geo.add_coastlines(
        ax1,
         colorName = "red",
          faceOpac = 0.5,
             level = 5,
         linewidth = 1.0,
        resolution = "i",
    )
    pyguymer3.geo.add_coastlines(
        ax1,
         colorName = "red",
          faceOpac = 0.5,
             level = 6,
         linewidth = 1.0,
        resolution = "i",
    )

    # **************************************************************************

    # Initialize dictionary and list ...
    data = {}
    labels = []
    lines = []

    # Loop over number of angles ...
    for iang, nang in enumerate([9, 17, 33, 65, 129, 257]):
        # Create short-hand ...
        color = f"C{iang:d}"

        # Loop over distances ...
        for dist in range(10, 90, 10):
            # Determine the step count ...
            istep = ((1000 * dist) // 1250) - 1                                 # [#]

            # Deduce directory name ...
            dname = f"res=i_cons=2.00e+00_tol=1.00e-10/nang={nang:d}_prec=1.25e+03/freqLand=768_freqSimp=768_lon={lon:+011.6f}_lat={lat:+010.6f}/ship"

            # Deduce file name and skip if it is missing ...
            fname = f"{dname}/istep={istep:06d}.wkb.gz"
            if not os.path.exists(fname):
                continue

            print(f"Plotting \"{fname}\" ...")

            # Load Polygon ...
            with gzip.open(fname, mode = "rb") as gzObj:
                ship = shapely.wkb.loads(gzObj.read())

            # Populate dictionary ...
            key = f"{dist:,d}km"
            if key not in data:
                data[key] = {
                    "nang" : [],                                                # [#]
                    "area" : [],                                                # [°2]
                }
            data[key]["nang"].append(nang)                                      # [#]
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
            if f"{nang:d} Angles" not in labels:
                # Add an entry to the legend ...
                labels.append(f"{nang:d} Angles")
                lines.append(matplotlib.lines.Line2D([], [], color = color))

            # Clean up ...
            del ship

    # Plot the starting location ...
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
        nang = numpy.array(data[key]["nang"])                                   # [#]
        area = numpy.array(data[key]["area"])                                   # [°2]

        # Convert to ratio ...
        area /= area[-1]

        # Convert to percentage ...
        area *= 100.0                                                           # [%]

        # Plot data ...
        ax2.plot(
            nang,
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
    )

    # Configure axis ...
    ax2.axhspan(
        99,
        101,
        color = (0.0, 1.0, 0.0, 0.25),
    )
    ax2.grid()
    ax2.legend(loc = "lower right")
    ax2.semilogx()
    ax2.set_xlabel("Number Of Angles")
    # ax2.set_xticks(                                                             # MatPlotLib ≥ 3.5.0
    #     [8, 16, 32, 64, 128, 256],                                              # MatPlotLib ≥ 3.5.0
    #     labels = [8, 16, 32, 64, 128, 256],                                     # MatPlotLib ≥ 3.5.0
    # )                                                                           # MatPlotLib ≥ 3.5.0
    ax2.set_xticks([8, 16, 32, 64, 128, 256])                                   # MatPlotLib < 3.5.0
    ax2.set_xticklabels([8, 16, 32, 64, 128, 256])                              # MatPlotLib < 3.5.0
    ax2.set_ylabel("Euclidean Area [%]")
    ax2.set_ylim(90, 102)
    ax2.set_yticks(range(90, 103))

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("compareBufferAngularResolutions.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image("compareBufferAngularResolutions.png", strip = True)
