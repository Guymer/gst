#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.10/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import glob
    import math
    import os

    # Import special modules ...
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

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.image
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

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
        # Study convergence (changing just "nang" and "prec") ...
        (2,  9, 5000,),
        (2, 17, 2500,),
        (2, 33, 1250,),
    ]

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (9, 6))

    # Create axis ...
    ax = fg.add_subplot()

    # **************************************************************************

    # Loop over combinations ...
    for colour, (cons, nang, prec) in enumerate(combs):
        print(f"Processing \"cons={cons:.2e}, nang={nang:d}, prec={prec:.2e}\" ...")

        # Deduce expected run time increase ...
        scaleFactor = (float(nang) / float(combs[0][1])) * (float(combs[0][2]) / float(prec))

        # **********************************************************************

        # Create short-hands ...
        # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
        freqLand = 24 * 40000 // prec                                           # [#]
        freqSimp = 40000 // prec                                                # [#]

        # Deduce directory name and find all limit files ...
        dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/nang={nang:d}_prec={prec:.2e}/freqLand={freqLand:d}_freqSimp={freqSimp:d}_lon={lon:+011.6f}_lat={lat:+010.6f}/limit"
        fnames = sorted(glob.glob(f"{dname}/istep=??????.wkb.gz"))

        # Create a list of the creation times of the limit files ...
        times = []                                                              # [s]
        for i, fname in enumerate(fnames):
            times.append(os.stat(fname).st_ctime)                               # [s]

        # Initialize counter and lists ...
        day = 0                                                                 # [day]
        calcDur = []                                                            # [s/step]
        sailingDur = []                                                         # [day]
        tmpCalcDur = []                                                         # [s/step]
        tmpSailingDur = []                                                      # [day]

        # Loop over limit files and their creation times ...
        for i in range(1, len(fnames)):
            # Extract step number, calculate distance and duration ...
            istep = int(fnames[i].split("/")[-1].split(".")[0].split("=")[1])   # [#]
            dist = istep * prec                                                 # [m]
            dur = float(dist) / (1852.0 * speed * 24.0)                         # [day]

            # Check if this was the first step of a new run ...
            if math.floor(dur) != day:
                # Increment counter and skip ...
                day += 1                                                        # [#]
                continue

            # Append values to lists ...
            tmpCalcDur.append(times[i] - times[i - 1])                          # [s/step]
            tmpSailingDur.append(dur)                                           # [day]

            # Check if this was a simplification step ...
            if (istep + 1) % freqSimp == 0:
                # Convert lists to arrays ...
                tmpCalcDur = numpy.array(tmpCalcDur)                            # [s/step]
                tmpSailingDur = numpy.array(tmpSailingDur)                      # [day]

                # Append values to lists ...
                calcDur.append(pyguymer3.mean(tmpCalcDur))                      # [s/step]
                sailingDur.append(pyguymer3.mean(tmpSailingDur))                # [day]

                # Re-initialize lists ...
                tmpCalcDur = []                                                 # [s/step]
                tmpSailingDur = []                                              # [day]

        # Clean up ...
        del tmpCalcDur, tmpSailingDur

        # Convert lists to arrays ...
        calcDur = numpy.array(calcDur)                                          # [s/step]
        sailingDur = numpy.array(sailingDur)                                    # [day]

        # Create list of keys which do not include the discontinuities from
        # restarting the command or revaluating the land ...
        keys = sailingDur.size * [True]
        for i in range(1, sailingDur.size - 1):
            if (calcDur[i] / calcDur[i - 1]) > 2.5 and (calcDur[i] / calcDur[i + 1]) > 2.5:
                if calcDur[i] / scaleFactor > 50.0:
                    keys[i] = False

        # **********************************************************************

        # Plot data ...
        ax.plot(
            sailingDur[keys],
            calcDur[keys] / scaleFactor,
            color = f"C{colour:d}",
            label = f"(cons={cons:d}, nang={nang:d}, prec={prec:d}) ÷ {scaleFactor:.2f}",
        )

        # Clean up ...
        del calcDur, sailingDur

    # **************************************************************************

    # Configure axis ...
    ax.grid()
    ax.legend(loc = "upper right")
    ax.set_xlabel("Sailing Duration [days]")
    ax.set_xlim(0.0, 24.1)
    ax.set_ylabel("(Equivalent) Average Calculation Duration [s/step]")
    ax.set_ylim(0.0, 150.0)

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("timings.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image("timings.png", strip = True)
