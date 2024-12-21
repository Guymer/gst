#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
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

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.image
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # **************************************************************************

    # Define function ...
    def meanWithoutOutlier(oldArr, /):
        """
        In this scenario, the user may have cancelled "run.py" mid-calculation
        and then restarted it at a later date. Therefore, if purely looking at
        the filesystem times, then one of the step durations will be much longer
        than the rest. Let's try and recover "the true" average step duration
        (assuming only one cancellation/restart per array).
        """

        # Find mean and standard deviation of the old array ...
        oldMean = pyguymer3.mean(oldArr)
        oldStddev = pyguymer3.stddev(oldArr)

        # Check if the standard deviation is wider than the mean ...
        if oldStddev > oldMean:
            # Create a new array without the maximum value ...
            newArr = oldArr[oldArr.argsort()][:-1]

            # Return new mean ...
            return pyguymer3.mean(newArr)

        # Return old mean ...
        return oldMean

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

    # Create axes ...
    axL = fg.add_subplot(1, 2, 1)
    axR = fg.add_subplot(1, 2, 2)

    # **************************************************************************

    # Loop over combinations ...
    for colour, (cons, nAng, prec) in enumerate(combs):
        print(f"Processing \"cons={cons:.2e}, nAng={nAng:d}, prec={prec:.2e}\" ...")

        # Deduce expected run time increase ...
        # NOTE: The logic here is:
        #         * it will take "nAng" times longer each step due to more
        #           angles around each corner; and
        #         * it will take "prec" times longer each step due to more
        #           points along each line.
        scaleFactor = (float(nAng) / float(combs[0][1])) * (float(combs[0][2]) / float(prec))

        # **********************************************************************

        # Create short-hands ...
        # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
        freqLand = 24 * 40000 // prec                                           # [#]
        freqSimp = 40000 // prec                                                # [#]

        # Deduce directory name and find all limit files ...
        dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/local=F_nAng={nAng:d}_prec={prec:.2e}/freqLand={freqLand:d}_freqSimp={freqSimp:d}_lon={lon:+011.6f}_lat={lat:+010.6f}/limit"
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
            # Extract step number and duration ...
            istep = int(fnames[i].split("/")[-1].split(".")[0].split("=")[1])   # [#]
            dur = float(istep * prec) / (1852.0 * speed * 24.0)                 # [day]

            # Check if this was the first step of a new run ...
            if math.floor(dur) != day:
                # Increment counter and skip ...
                day += 1                                                        # [#]
                continue

            # Append values to lists ...
            tmpCalcDur.append(times[i] - times[i - 1])                          # [s/step]
            tmpSailingDur.append(dur)                                           # [day]

            # ******************************************************************

            # Check if this was a simplification step ...
            if (istep + 1) % freqSimp == 0:
                # Convert lists to arrays ...
                tmpCalcDur = numpy.array(tmpCalcDur)                            # [s/step]
                tmpSailingDur = numpy.array(tmpSailingDur)                      # [day]

                # Append values to lists ...
                calcDur.append(meanWithoutOutlier(tmpCalcDur))                  # [s/step]
                sailingDur.append(pyguymer3.mean(tmpSailingDur))                # [day]

                # Re-initialize lists ...
                tmpCalcDur = []                                                 # [s/step]
                tmpSailingDur = []                                              # [day]

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

        # Replace arrays with versions without the discontinuities ...
        calcDur = calcDur[keys]                                                 # [s/step]
        sailingDur = sailingDur[keys]                                           # [day]

        # **********************************************************************

        # Plot data ...
        axL.plot(
            sailingDur,
            calcDur / scaleFactor,
            color = f"C{colour:d}",
            label = f"(cons={cons:d}, nAng={nAng:d}, prec={prec:d}) ÷ {scaleFactor:.2f}",
        )

        # **********************************************************************

        # Initialize arrays ...
        cumCalcDur = numpy.zeros(calcDur.size + 1, dtype = numpy.float64)       # [s/step]
        cumSailingDur = numpy.zeros(sailingDur.size + 1, dtype = numpy.float64) # [day]

        # Calculate cumulative sailing duration ...
        for istep in range(sailingDur.size):
            cumCalcDur[istep + 1] = cumCalcDur[istep] + calcDur[istep]          # [s/step]
            cumSailingDur[istep + 1] = sailingDur[istep]                        # [day]

        # Plot data ...
        axR.plot(
            cumSailingDur,
            cumCalcDur / cumCalcDur[-1],
            color = f"C{colour:d}",
            label = f"cons={cons:d}, nAng={nAng:d}, prec={prec:d}",
        )

    # **************************************************************************

    # Configure axis ...
    axL.grid()
    axL.legend(loc = "upper right")
    axL.set_xlabel("Sailing Duration [days]")
    axL.set_xlim(0.0, 24.1)
    axL.set_xticks(range(25))
    axL.set_ylabel("(Equivalent) Average Calculation Duration [s/step]")
    axL.set_ylim(0.0, 150.0)

    # Configure axis ...
    axR.grid()
    axR.legend(loc = "upper left")
    axR.set_xlabel("Sailing Duration [days]")
    axR.set_xlim(0.0, 24.1)
    axR.set_xticks(range(25))
    axR.set_ylabel("Normalized Cumulative Calculation Duration")
    axR.set_ylim(0.0, 1.0)

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("timings.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image("timings.png", strip = True)
