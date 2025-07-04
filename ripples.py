#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import glob
    import gzip
    import os
    import shutil
    import subprocess
    import sysconfig

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
            description = "Show the ripples spreading.",
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
          help = "don't run \"run.py\"",
    )
    parser.add_argument(
        "--plot",
        action = "store_true",
          help = "make maps and animation",
    )
    args = parser.parse_args()

    # **************************************************************************

    # Define resolution ...
    res = "i"

    # Define starting location ...
    lon = -1.0                                                                  # [°]
    lat = 50.5                                                                  # [°]

    # Define combinations ...
    combs = [
        # Study convergence (changing just "nAng" and "prec") ...
        (2,  9, 5000, (1.0, 0.0, 0.0, 1.0),),
        (2, 17, 2500, (0.0, 1.0, 0.0, 1.0),),
        (2, 33, 1250, (0.0, 0.0, 1.0, 1.0),),

        # Study convergence (changing "cons", "nAng" and "prec") ...
        # (2,  9, 5000, (1.0, 0.0, 0.0, 1.0),),
        # (4, 17, 2500, (0.0, 1.0, 0.0, 1.0),),
        # (8, 33, 1250, (0.0, 0.0, 1.0, 1.0),),

        # With "nAng=17" and "prec=2500", is "cons=2" good enough?
        # (2, 17, 2500, (1.0, 0.0, 0.0, 1.0),),
        # (4, 17, 2500, (0.0, 1.0, 0.0, 1.0),),

        # With "nAng=33" and "prec=1250", is "cons=2" good enough?
        # (2, 33, 1250, (1.0, 0.0, 0.0, 1.0),),
        # (8, 33, 1250, (0.0, 1.0, 0.0, 1.0),),
    ]

    # Determine output directory and make it if it is missing ...
    outDir = "_".join(
        [
            "cons=" + ",".join([f"{cons:.2e}" for cons, nAng, prec, color in combs]),
            "nAng=" + ",".join([f"{nAng:d}" for cons, nAng, prec, color in combs]),
            "prec=" + ",".join([f"{prec:.2e}" for cons, nAng, prec, color in combs]),
        ]
    )
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    if not os.path.exists(f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}"):
        os.mkdir(f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}")

    # **************************************************************************

    # Create the initial starting Point ...
    ship = shapely.geometry.point.Point(lon, lat)

    # **************************************************************************

    # Loop over days ...
    for dur in range(1, 25):
        # Loop over combinations ...
        for cons, nAng, prec, color in combs:
            # Create short-hands ...
            # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
            freqLand = 24 * 40000 // prec                                       # [#]
            freqPlot = 40000 // prec                                            # [#]
            freqSimp = 40000 // prec                                            # [#]

            # Populate GST command ...
            cmd = [
                f"python{sysconfig.get_python_version()}", "run.py",
                f"{lon:+.1f}", f"{lat:+.1f}", "20.0",
                "--conservatism", f"{cons:.1f}",    # LOOP VARIABLE
                "--duration", f"{dur:.1f}",         # LOOP VARIABLE
                "--freqLand", f"{freqLand:d}",      # ~daily land re-evaluation
                "--freqPlot", f"{freqPlot:d}",      # ~hourly plotting
                "--freqSimp", f"{freqSimp:d}",      # ~hourly simplification
                "--nAng", f"{nAng:d}",              # LOOP VARIABLE
                "--precision", f"{prec:.1f}",       # LOOP VARIABLE
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

    # Loop over combinations ...
    for cons, nAng, prec, color in combs:
        # Create short-hands ...
        # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
        freqLand = 24 * 40000 // prec                                           # [#]
        freqSimp = 40000 // prec                                                # [#]

        # Deduce directory name ...
        dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/local=F_nAng={nAng:d}_prec={prec:.2e}/freqLand={freqLand:d}_freqSimp={freqSimp:d}_lon={lon:+011.6f}_lat={lat:+010.6f}/limit"

        # Find the maximum distance that has been calculated so far ...
        fname = sorted(glob.glob(f"{dname}/istep=??????.wkb.gz"))[-1]
        istep = int(os.path.basename(fname).split("=")[1].split(".")[0])        # [#]

        # Create short-hands ...
        maxDist = float(istep * prec)                                           # [m]
        maxDur = maxDist / (1852.0 * 20.0)                                      # [hr]

        print(f" > {0.001 * maxDist:,.2f} kilometres of sailing is available (which is {maxDur / 24.0:,.4f} days).")

    # **************************************************************************

    # Initialize list ...
    frames = []

    # Loop over distances ...
    for dist in range(5, 30005, 5):
        # Deduce PNG name, if it exists then append it to the list and skip ...
        frame = f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}/dist={dist:05d}.png"
        if os.path.exists(frame):
            frames.append(frame)
            continue

        # **********************************************************************

        # Initialize list ...
        fnames = []

        # Loop over combinations ...
        for cons, nAng, prec, color in combs:
            # Skip if this distance cannot exist (because the precision is too
            # coarse) and determine the step count ...
            if (1000 * dist) % prec != 0:
                continue
            istep = ((1000 * dist) // prec) - 1                                 # [#]

            # Create short-hands ...
            # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
            freqLand = 24 * 40000 // prec                                       # [#]
            freqSimp = 40000 // prec                                            # [#]

            # Deduce directory name ...
            dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/local=F_nAng={nAng:d}_prec={prec:.2e}/freqLand={freqLand:d}_freqSimp={freqSimp:d}_lon={lon:+011.6f}_lat={lat:+010.6f}/limit"

            # Deduce file name and skip if it is missing ...
            fname = f"{dname}/istep={istep + 1:06d}.wkb.gz"
            if not os.path.exists(fname):
                continue

            # Append it to the list ...
            fnames.append(fname)

        # Skip this frame if there are not enough files ...
        if len(fnames) != len(combs):
            continue

        # **********************************************************************

        print(f"Making \"{frame}\" ...")

        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (12.8, 7.2))

        # Create axis ...
        # NOTE: Really, I should be plotting "allLands" to be consistent with
        #       the ships, however, as each ship (potentially) is using
        #       different collections of land then I will just use the raw GSHHG
        #       dataset instead.
        ax = pyguymer3.geo.add_axis(
            fg,
            coastlines_resolution = res,
        )

        # Configure axis ...
        pyguymer3.geo.add_map_background(
            ax,
                  name = "shaded-relief",
            resolution = "large8192px",
        )

        # Initialize lists ...
        labels = []
        lines = []

        # Loop over combinations/files ...
        for (cons, nAng, prec, color), fname in zip(combs, fnames, strict = True):
            print(f" > Loading \"{fname}\" ...")

            # Load [Multi]LineString ...
            with gzip.open(fname, mode = "rb") as gzObj:
                limit = shapely.wkb.loads(gzObj.read())

            # Plot [Multi]LineString ...
            # NOTE: Given how "limit" was made, we know that there aren't any
            #       invalid LineStrings, so don't bother checking for them.
            ax.add_geometries(
                pyguymer3.geo.extract_lines(limit, onlyValid = False),
                cartopy.crs.PlateCarree(),
                edgecolor = color,
                facecolor = "none",
                linewidth = 1.0,
            )

            # Add an entry to the legend ...
            labels.append(f"cons={cons:d}, nAng={nAng:d}, prec={prec:d}")
            lines.append(matplotlib.lines.Line2D([], [], color = color))

        # Check that the distance isn't too large ...
        if 1000.0 * float(dist) <= 0.5 * pyguymer3.CIRCUMFERENCE_OF_EARTH:
            # Calculate the maximum distance the ship could have got to ...
            maxShip = pyguymer3.geo.buffer(
                ship,
                1000.0 * float(dist),
                fill = +1.0,
                nAng = 361,
                simp = -1.0,
            )

            # Plot [Multi]Polygon ...
            ax.add_geometries(
                pyguymer3.geo.extract_polys(maxShip, onlyValid = False, repair = False),
                cartopy.crs.PlateCarree(),
                edgecolor = "gold",
                facecolor = "none",
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

        # Create short-hand ...
        dur = 1000.0 * float(dist) / (1852.0 * 20.0 * 24.0)                     # [day]

        # Configure axis ...
        ax.legend(
            lines,
            labels,
            loc = "lower left",
        )
        ax.set_title(
            f"{dist:6,d} km ({dur:5.2f} days)",
            fontfamily = "monospace",
                   loc = "right",
        )

        # Configure figure ...
        fg.tight_layout()

        # Save figure ...
        fg.savefig(frame)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimise_image(frame, strip = True)

        # Append frame to list ...
        frames.append(frame)

    # **************************************************************************

    print(f"Making \"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}.mp4\" ...")

    # Save 60fps MP4 ...
    vname = pyguymer3.media.images2mp4(
        frames,
        fps = 60.0,
    )
    shutil.move(vname, f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}.mp4")

    # Set maximum sizes ...
    # NOTE: By inspection, the PNG frames are 3,840 px wide.
    maxSizes = [512, 1024, 2048]                                                # [px]

    # Loop over maximum sizes ...
    for maxSize in maxSizes:
        print(f"Making \"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}{maxSize:04d}px.mp4\" ...")

        # Save 60fps MP4 ...
        vname = pyguymer3.media.images2mp4(
            frames,
                     fps = 60.0,
            screenHeight = maxSize,
             screenWidth = maxSize,
        )
        shutil.move(vname, f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}{maxSize:04d}px.mp4")

    # **************************************************************************

    # Initialize list ...
    frames = []

    # Loop over distances ...
    for dist in range(3290, 5185, 5):
        # Deduce PNG name, if it exists then append it to the list and skip ...
        frame = f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}/dist={dist:05d}_NovayaZemlya.png"
        if os.path.exists(frame):
            frames.append(frame)
            continue

        # **********************************************************************

        # Initialize list ...
        fnames = []

        # Loop over combinations ...
        for cons, nAng, prec, color in combs:
            # Skip if this distance cannot exist (because the precision is too
            # coarse) and determine the step count ...
            if (1000 * dist) % prec != 0:
                continue
            istep = ((1000 * dist) // prec) - 1                                 # [#]

            # Create short-hands ...
            # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
            freqLand = 24 * 40000 // prec                                       # [#]
            freqSimp = 40000 // prec                                            # [#]

            # Deduce directory name ...
            dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/local=F_nAng={nAng:d}_prec={prec:.2e}/freqLand={freqLand:d}_freqSimp={freqSimp:d}_lon={lon:+011.6f}_lat={lat:+010.6f}/limit"

            # Deduce file name and skip if it is missing ...
            fname = f"{dname}/istep={istep + 1:06d}.wkb.gz"
            if not os.path.exists(fname):
                continue

            # Append it to the list ...
            fnames.append(fname)

        # Skip this frame if there are not enough files ...
        if len(fnames) != len(combs):
            continue

        # **********************************************************************

        print(f"Making \"{frame}\" ...")

        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

        # Create axis ...
        # NOTE: Really, I should be plotting "allLands" to be consistent with
        #       the ships, however, as each ship (potentially) is using
        #       different collections of land then I will just use the raw GSHHG
        #       dataset instead.
        ax = pyguymer3.geo.add_axis(
            fg,
            coastlines_resolution = res,
                             dist = 400.0e3,
                              lat = 73.5,
                              lon = 60.0,
        )

        # Configure axis ...
        pyguymer3.geo.add_map_background(
            ax,
                  name = "shaded-relief",
            resolution = "large8192px",
        )

        # Initialize lists ...
        labels = []
        lines = []

        # Loop over combinations/files ...
        for (cons, nAng, prec, color), fname in zip(combs, fnames, strict = True):
            print(f" > Loading \"{fname}\" ...")

            # Load [Multi]LineString ...
            with gzip.open(fname, mode = "rb") as gzObj:
                limit = shapely.wkb.loads(gzObj.read())

            # Plot [Multi]LineString ...
            # NOTE: Given how "limit" was made, we know that there aren't any
            #       invalid LineStrings, so don't bother checking for them.
            ax.add_geometries(
                pyguymer3.geo.extract_lines(limit, onlyValid = False),
                cartopy.crs.PlateCarree(),
                edgecolor = color,
                facecolor = "none",
                linewidth = 1.0,
            )

            # Add an entry to the legend ...
            labels.append(f"cons={cons:d}, nAng={nAng:d}, prec={prec:d}")
            lines.append(matplotlib.lines.Line2D([], [], color = color))

        # Check that the distance isn't too large ...
        if 1000.0 * float(dist) <= 0.5 * pyguymer3.CIRCUMFERENCE_OF_EARTH:
            # Calculate the maximum distance the ship could have got to ...
            maxShip = pyguymer3.geo.buffer(
                ship,
                1000.0 * float(dist),
                fill = +1.0,
                nAng = 361,
                simp = -1.0,
            )

            # Plot [Multi]Polygon ...
            ax.add_geometries(
                pyguymer3.geo.extract_polys(maxShip, onlyValid = False, repair = False),
                cartopy.crs.PlateCarree(),
                edgecolor = "gold",
                facecolor = "none",
                linewidth = 1.0,
            )

        # Create short-hand ...
        dur = 1000.0 * float(dist) / (1852.0 * 20.0 * 24.0)                     # [day]

        # Configure axis ...
        ax.legend(
            lines,
            labels,
            loc = "lower right",
        )
        ax.set_title(
            f"{dist:6,d} km ({dur:5.2f} days)",
            fontfamily = "monospace",
                   loc = "right",
        )

        # Configure figure ...
        fg.tight_layout()

        # Save figure ...
        fg.savefig(frame)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimise_image(frame, strip = True)

        # Append frame to list ...
        frames.append(frame)

    # **************************************************************************

    print(f"Making \"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}_NovayaZemlya.mp4\" ...")

    # Save 60fps MP4 ...
    vname = pyguymer3.media.images2mp4(
        frames,
        fps = 60.0,
    )
    shutil.move(vname, f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}_NovayaZemlya.mp4")

    # Set maximum sizes ...
    # NOTE: By inspection, the PNG frames are 2,160 px tall/wide.
    maxSizes = [512, 1024, 2048]                                                # [px]

    # Loop over maximum sizes ...
    for maxSize in maxSizes:
        print(f"Making \"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}_NovayaZemlya{maxSize:04d}px.mp4\" ...")

        # Save 60fps MP4 ...
        vname = pyguymer3.media.images2mp4(
            frames,
                     fps = 60.0,
            screenHeight = maxSize,
             screenWidth = maxSize,
        )
        shutil.move(vname, f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}_NovayaZemlya{maxSize:04d}px.mp4")

    # **************************************************************************

    # Initialize list ...
    frames = []

    # Loop over distances ...
    for dist in range(14150, 15185, 5):
        # Deduce PNG name, if it exists then append it to the list and skip ...
        frame = f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}/dist={dist:05d}_BocaDelGuafo.png"
        if os.path.exists(frame):
            frames.append(frame)
            continue

        # **********************************************************************

        # Initialize list ...
        fnames = []

        # Loop over combinations ...
        for cons, nAng, prec, color in combs:
            # Skip if this distance cannot exist (because the precision is too
            # coarse) and determine the step count ...
            if (1000 * dist) % prec != 0:
                continue
            istep = ((1000 * dist) // prec) - 1                                 # [#]

            # Create short-hands ...
            # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
            freqLand = 24 * 40000 // prec                                       # [#]
            freqSimp = 40000 // prec                                            # [#]

            # Deduce directory name ...
            dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/local=F_nAng={nAng:d}_prec={prec:.2e}/freqLand={freqLand:d}_freqSimp={freqSimp:d}_lon={lon:+011.6f}_lat={lat:+010.6f}/limit"

            # Deduce file name and skip if it is missing ...
            fname = f"{dname}/istep={istep + 1:06d}.wkb.gz"
            if not os.path.exists(fname):
                continue

            # Append it to the list ...
            fnames.append(fname)

        # Skip this frame if there are not enough files ...
        if len(fnames) != len(combs):
            continue

        # **********************************************************************

        print(f"Making \"{frame}\" ...")

        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

        # Create axis ...
        # NOTE: Really, I should be plotting "allLands" to be consistent with
        #       the ships, however, as each ship (potentially) is using
        #       different collections of land then I will just use the raw GSHHG
        #       dataset instead.
        ax = pyguymer3.geo.add_axis(
            fg,
            coastlines_resolution = res,
                             dist = 300.0e3,
                              lat = -44.0,
                              lon = -74.0,
        )

        # Configure axis ...
        pyguymer3.geo.add_map_background(
            ax,
                  name = "shaded-relief",
            resolution = "large8192px",
        )

        # Initialize lists ...
        labels = []
        lines = []

        # Loop over combinations/files ...
        for (cons, nAng, prec, color), fname in zip(combs, fnames, strict = True):
            print(f" > Loading \"{fname}\" ...")

            # Load [Multi]LineString ...
            with gzip.open(fname, mode = "rb") as gzObj:
                limit = shapely.wkb.loads(gzObj.read())

            # Plot [Multi]LineString ...
            # NOTE: Given how "limit" was made, we know that there aren't any
            #       invalid LineStrings, so don't bother checking for them.
            ax.add_geometries(
                pyguymer3.geo.extract_lines(limit, onlyValid = False),
                cartopy.crs.PlateCarree(),
                edgecolor = color,
                facecolor = "none",
                linewidth = 1.0,
            )

            # Add an entry to the legend ...
            labels.append(f"cons={cons:d}, nAng={nAng:d}, prec={prec:d}")
            lines.append(matplotlib.lines.Line2D([], [], color = color))

        # Check that the distance isn't too large ...
        if 1000.0 * float(dist) <= 0.5 * pyguymer3.CIRCUMFERENCE_OF_EARTH:
            # Calculate the maximum distance the ship could have got to ...
            maxShip = pyguymer3.geo.buffer(
                ship,
                1000.0 * float(dist),
                fill = +1.0,
                nAng = 361,
                simp = -1.0,
            )

            # Plot [Multi]Polygon ...
            ax.add_geometries(
                pyguymer3.geo.extract_polys(maxShip, onlyValid = False, repair = False),
                cartopy.crs.PlateCarree(),
                edgecolor = "gold",
                facecolor = "none",
                linewidth = 1.0,
            )

        # Create short-hand ...
        dur = 1000.0 * float(dist) / (1852.0 * 20.0 * 24.0)                     # [day]

        # Configure axis ...
        ax.legend(
            lines,
            labels,
            loc = "lower right",
        )
        ax.set_title(
            f"{dist:6,d} km ({dur:5.2f} days)",
            fontfamily = "monospace",
                   loc = "right",
        )

        # Configure figure ...
        fg.tight_layout()

        # Save figure ...
        fg.savefig(frame)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimise_image(frame, strip = True)

        # Append frame to list ...
        frames.append(frame)

    # **************************************************************************

    print(f"Making \"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}_BocaDelGuafo.mp4\" ...")

    # Save 60fps MP4 ...
    vname = pyguymer3.media.images2mp4(
        frames,
        fps = 60.0,
    )
    shutil.move(vname, f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}_BocaDelGuafo.mp4")

    # Set maximum sizes ...
    # NOTE: By inspection, the PNG frames are 2,160 px tall/wide.
    maxSizes = [512, 1024, 2048]                                                # [px]

    # Loop over maximum sizes ...
    for maxSize in maxSizes:
        print(f"Making \"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}_BocaDelGuafo{maxSize:04d}px.mp4\" ...")

        # Save 60fps MP4 ...
        vname = pyguymer3.media.images2mp4(
            frames,
                     fps = 60.0,
            screenHeight = maxSize,
             screenWidth = maxSize,
        )
        shutil.move(vname, f"{outDir}/res={res}_lon={lon:+011.6f}_lat={lat:+010.6f}_BocaDelGuafo{maxSize:04d}px.mp4")
