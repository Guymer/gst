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

    # Loop over precisions ...
    for prec in [625, 1250, 2500, 5000, 10000, 20000]:
        # Create short-hand ...
        # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
        freq = 24 * 40000 // prec                                               # [#]

        # Populate GST command ...
        cmd = [
            "python3.11", "run.py",
            f"{lon:+.1f}", f"{lat:+.1f}", "20.0",
            "--duration", "0.09",           # some sailing (20 knots * 0.09 days = 80.01 kilometres)
            "--freqLand", f"{freq:d}",      # ~daily land re-evaluation
            "--freqSimp", f"{freq:d}",      # ~daily simplification
            "--nang", "257",                # converged number of angles (from "compareBufferAngularResolutions.py")
            "--precision", f"{prec:.1f}",   # LOOP VARIABLE
            "--resolution", "i",            # intermediate coastline resolution
        ]

        print(f'Running "{" ".join(cmd)}" ...')

        # Run GST ...
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
    fg = matplotlib.pyplot.figure(figsize = (4.0, 7.2))

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
        linewidth = 1.0,
    )

    # **************************************************************************

    # Initialize dictionary and list ...
    data = {}
    labels = []
    lines = []

    # Loop over precisions ...
    for iprec, prec in enumerate([625, 1250, 2500, 5000, 10000, 20000]):
        # Create short-hands ...
        # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
        color = f"C{iprec:d}"
        freq = 24 * 40000 // prec                                               # [#]

        # Loop over distances ...
        for dist in range(10, 90, 10):
            # Skip if this distance cannot exist (because the precision is too
            # coarse) and determine the step count ...
            if (1000 * dist) % prec != 0:
                continue
            istep = ((1000 * dist) // prec) - 1                                 # [#]

            # Deduce directory name ...
            dname = f"res=i_cons=2.00e+00_tol=1.00e-10/nang=257_prec={prec:.2e}/freqLand={freq:d}_freqSimp={freq:d}_lon={lon:+011.6f}_lat={lat:+010.6f}/ship"

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
                    "prec" : [],                                                # [m]
                    "area" : [],                                                # [°2]
                }
            data[key]["prec"].append(prec)                                      # [m]
            data[key]["area"].append(ship.area)                                 # [°2]

            # Plot Polygon ...
            ax1.add_geometries(
                [ship],
                cartopy.crs.PlateCarree(),
                edgecolor = color,
                facecolor = "none",
                linewidth = 1.0,
            )

            # Check if it is the first distance for this precision ...
            if f"{prec:,d}m" not in labels:
                # Add an entry to the legend ...
                labels.append(f"{prec:,d}m")
                lines.append(matplotlib.lines.Line2D([], [], color = color))

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
        prec = numpy.array(data[key]["prec"])                                   # [m]
        area = numpy.array(data[key]["area"])                                   # [°2]

        # Convert to ratio ...
        area /= area[0]

        # Convert to percentage ...
        area *= 100.0                                                           # [%]

        # Plot data ...
        ax2.plot(
            prec,
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
            alpha = 0.25,
        facecolor = "green",
    )
    ax2.grid()
    ax2.legend(loc = "lower right")
    ax2.semilogx()
    ax2.set_xlabel("Precision [m]")
    # ax2.set_xticks(                                                             # MatPlotLib ≥ 3.5.0
    #     [625, 1250, 2500, 5000, 10000, 20000],                                  # MatPlotLib ≥ 3.5.0
    #     labels = [625, 1250, 2500, 5000, 10000, 20000],                         # MatPlotLib ≥ 3.5.0
    # )                                                                           # MatPlotLib ≥ 3.5.0
    ax2.set_xticks([625, 1250, 2500, 5000, 10000, 20000])                       # MatPlotLib < 3.5.0
    ax2.set_xticklabels([625, 1250, 2500, 5000, 10000, 20000])                  # MatPlotLib < 3.5.0
    ax2.set_ylabel("Euclidean Area [%]")
    ax2.set_ylim(75, 102)
    ax2.set_yticks(range(75, 103))

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("compareBufferRadialResolutions.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image("compareBufferRadialResolutions.png", strip = True)
