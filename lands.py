#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.10/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import glob
    import gzip

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
        # NOTE: The logic here is:
        #         * there will be "nang" more points due to more angles around
        #           each corner; and
        #         * there will be "prec" more points due to more points along
        #           each line.
        scaleFactor = (float(nang) / float(combs[0][1])) * (float(combs[0][2]) / float(prec))

        # **********************************************************************

        # Create short-hands ...
        # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
        freqLand = 24 * 40000 // prec                                           # [#]
        freqSimp = 40000 // prec                                                # [#]

        # Deduce directory name and find all relevant land files ...
        dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/nang={nang:d}_prec={prec:.2e}/freqLand={freqLand:d}_freqSimp={freqSimp:d}_lon={lon:+011.6f}_lat={lat:+010.6f}/relevantLands"
        fnames = sorted(glob.glob(f"{dname}/istep=??????.wkb.gz"))

        # Initialize lists ...
        calcLength = []                                                         # [#]
        sailingDur = []                                                         # [#]

        # Loop over relevant land files ...
        for fname in fnames:
            # Extract step number ...
            istep = int(fname.split("/")[-1].split(".")[0].split("=")[1])       # [#]

            # Initialize length ...
            length = 0                                                          # [#]

            # Load [Multi]Polygon ...
            with gzip.open(fname, mode = "rb") as gzObj:
                relevantLands = shapely.wkb.loads(gzObj.read())

            # Loop over Polygons ...
            for poly in pyguymer3.geo.extract_polys(relevantLands, onlyValid = False):
                # Increment length ...
                length += len(poly.exterior.coords)                             # [#]

            # Add values to lists ...
            calcLength = calcLength + freqLand * [length]                       # [#]
            sailingDur = sailingDur + list(range(istep, istep + freqLand))      # [#]

        # Convert lists to arrays ...
        calcLength = numpy.array(calcLength)                                    # [#]
        sailingDur = numpy.array(sailingDur, dtype = numpy.float64)             # [#]

        # Convert step numbers to durations ...
        sailingDur *= float(prec) / (1852.0 * speed * 24.0)                     # [day]

        # **********************************************************************

        # Plot data ...
        ax.plot(
            sailingDur,
            calcLength / scaleFactor,
            color = f"C{colour:d}",
            label = f"(cons={cons:d}, nang={nang:d}, prec={prec:d}) ÷ {scaleFactor:.2f}",
        )

        # Clean up ...
        del calcLength, sailingDur

    # **************************************************************************

    # Configure axis ...
    ax.grid()
    ax.legend(loc = "upper right")
    ax.set_xlabel("Sailing Duration [days]")
    ax.set_xlim(0.0, 24.1)
    ax.set_xticks(range(25))
    ax.set_ylabel("(Equivalent) Number Of Points Along Coastlines [#]")
    ax.set_ylim(0.0, 45000.0)

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("lands.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image("lands.png", strip = True)
