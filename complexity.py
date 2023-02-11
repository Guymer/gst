#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.10/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import gzip
    import os
    import subprocess

    # Import special modules ...
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

    # **************************************************************************

    # Define resolution ...
    res = "i"

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

    # Loop over combinations ...
    for cons, nang, prec in combs:
        # Create short-hands ...
        # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
        freqLand = 24 * 40000 // prec                                           # [#]
        freqSimp = 40000 // prec                                                # [#]

        # Populate GST command ...
        cmd = [
            "python3.10", "run.py",
            f"{lon:+.1f}", f"{lat:+.1f}", "20.0",
            "--conservatism", f"{cons:.1f}",    # LOOP VARIABLE
            "--duration", "0.09",               # some sailing (20 knots * 0.09 days = 80.01 kilometres)
            "--freqLand", f"{freqLand:d}",      # ~daily land re-evaluation
            "--freqSimp", f"{freqSimp:d}",      # ~hourly simplification
            "--nang", f"{nang:d}",              # LOOP VARIABLE
            "--precision", f"{prec:.1f}",       # LOOP VARIABLE
            "--resolution", res,
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

    # **************************************************************************

    # Define axes ...
    nLon = 36                                                                   # [px]
    nLat = 18                                                                   # [px]
    lons = numpy.linspace(-180.0, +180.0, num = nLon + 1, dtype = numpy.float64)# [°]
    lats = numpy.linspace( +90.0,  -90.0, num = nLat + 1, dtype = numpy.float64)# [°]

    # Loop over combinations ...
    for cons, nang, prec in combs:
        # Initialize image ...
        hist = numpy.zeros((nLat, nLon), dtype = numpy.uint64)                  # [#]

        # Deduce directory name ...
        dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/nang={nang:d}_prec={prec:.2e}"

        # Deduce file name and skip if it is missing ...
        fname = f"{dname}/allLands.wkb.gz"
        if not os.path.exists(fname):
            continue

        print(f"Surveying \"{fname}\" ...")

        # Load [Multi]Polygon ...
        with gzip.open(fname, mode = "rb") as gzObj:
            allLands = shapely.wkb.loads(gzObj.read())

        # Loop over Polygons ...
        for allLand in pyguymer3.geo.extract_polys(allLands, onlyValid = False, repair = False):
            # Loop over coordinates in the exterior ring ...
            for coord in allLand.exterior.coords:
                # Find the pixel that this coordinate corresponds to ...
                iLon = min(nLon - 1, numpy.flatnonzero(lons <= coord[0])[-1])   # [px]
                iLat = min(nLat - 1, numpy.flatnonzero(lats >= coord[1])[-1])   # [px]

                # Increment image ...
                hist[iLat, iLon] += 1                                           # [#]

        print(f"Saving \"complexity_res={res}_cons={cons:.2e}_nang={nang:d}_prec={prec:.2e}.png\" ...")

        # Save image ...
        pyguymer3.image.save_array_as_image(
            hist,
            f"complexity_res={res}_cons={cons:.2e}_nang={nang:d}_prec={prec:.2e}.png",
               ct = "rainbow",
            scale = True,
        )
