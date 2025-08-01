#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import glob
    import gzip

    # Import special modules ...
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
        import shapely.geometry
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
            description = "Plot the number of points in the limit lines.",
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

    # **************************************************************************

    # Define resolution ...
    res = "i"

    # Define speed ...
    speed = 20.0                                                                # [NM/hr]

    # Define starting location ...
    lon = -1.0                                                                  # [°]
    lat = 50.5                                                                  # [°]

    # Define combinations ...
    combs = [
        # Study convergence (changing just "nAng" and "prec") ...
        (2,  9, 5000,),
        (2, 17, 2500,),
        (2, 33, 1250,),
    ]

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure()

    # Create axis ...
    ax = fg.add_subplot()

    # **************************************************************************

    # Loop over combinations ...
    for colour, (cons, nAng, prec) in enumerate(combs):
        print(f"Processing \"cons={cons:.2e}, nAng={nAng:d}, prec={prec:.2e}\" ...")

        # Deduce expected run time increase ...
        # NOTE: The logic here is:
        #         * there will be "nAng" more points due to more angles around
        #           each corner; and
        #         * there will be "prec" more points due to more points along
        #           each line.
        scaleFactor = (float(nAng) / float(combs[0][1])) * (float(combs[0][2]) / float(prec))

        # **********************************************************************

        # Create short-hands ...
        # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
        freqLand = 24 * 40000 // prec                                           # [#]
        freqSimp = 40000 // prec                                                # [#]

        # Deduce directory name and find all limit files ...
        dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/local=F_nAng={nAng:d}_prec={prec:.2e}/freqLand={freqLand:d}_freqSimp={freqSimp:d}_lon={lon:+011.6f}_lat={lat:+010.6f}/limit"
        fnames = sorted(glob.glob(f"{dname}/istep=??????.wkb.gz"))

        # Initialize lists ...
        calcLength = []                                                         # [#]
        sailingDur = []                                                         # [day]
        tmpCalcLength = []                                                      # [#]
        tmpSailingDur = []                                                      # [day]

        # Loop over limit files ...
        for fname in fnames:
            # Extract step number and duration ...
            istep = int(fname.split("/")[-1].split(".")[0].split("=")[1])       # [#]
            dur = float(istep * prec) / (1852.0 * speed * 24.0)                 # [day]

            # Initialize length ...
            length = 0                                                          # [#]

            # Load [Multi]LineString ...
            with gzip.open(fname, mode = "rb") as gzObj:
                limit = shapely.wkb.loads(gzObj.read())

            # Loop over LineString ...
            for line in pyguymer3.geo.extract_lines(limit, onlyValid = False):
                # Increment length ...
                length += len(line.coords)                                      # [#]

            # Append values to lists ...
            tmpCalcLength.append(length)                                        # [#]
            tmpSailingDur.append(dur)                                           # [day]

            # ******************************************************************

            # Check if this was a simplification step ...
            if (istep + 1) % freqSimp == 0:
                # Convert lists to arrays ...
                tmpCalcLength = numpy.array(tmpCalcLength).astype(numpy.float64)# [#]
                tmpSailingDur = numpy.array(tmpSailingDur)                      # [day]

                # Append values to lists ...
                calcLength.append(pyguymer3.mean(tmpCalcLength))                # [#]
                sailingDur.append(pyguymer3.mean(tmpSailingDur))                # [day]

                # Re-initialize lists ...
                tmpCalcLength = []                                              # [#]
                tmpSailingDur = []                                              # [day]

        # Convert lists to arrays ...
        calcLength = numpy.array(calcLength)                                    # [#]
        sailingDur = numpy.array(sailingDur)                                    # [day]

        # **********************************************************************

        # Plot data ...
        ax.plot(
            sailingDur,
            calcLength / scaleFactor,
            color = f"C{colour:d}",
            label = f"(cons={cons:d}, nAng={nAng:d}, prec={prec:d}) ÷ {scaleFactor:.2f}",
        )

    # **************************************************************************

    # Configure axis ...
    ax.grid()
    ax.legend(loc = "upper right")
    ax.set_xlabel("Sailing Duration [days]")
    ax.set_xlim(0.0, 24.1)
    ax.set_xticks(range(25))
    ax.set_ylabel("(Equivalent) Number Of Points Along Limit [#]")
    ax.set_ylim(0.0, 130000.0)

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("lengths.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimise_image(
        "lengths.png",
          debug = args.debug,
          strip = True,
        timeout = args.timeout,
    )
