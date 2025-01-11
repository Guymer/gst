#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import gzip
    import json
    import math
    import os
    import subprocess

    # Import special modules ...
    try:
        import numpy
    except:
        raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
    try:
        import PIL
        import PIL.Image
        PIL.Image.MAX_IMAGE_PIXELS = 1024 * 1024 * 1024                         # [px]
        import PIL.ImageDraw
    except:
        raise Exception("\"PIL\" is not installed; run \"pip install --user Pillow\"") from None
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
            description = "Show the complexity of coastline boundaries for different sailing configurations.",
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
    args = parser.parse_args()

    # **************************************************************************

    # Define resolution ...
    res = "i"

    # Define combinations ...
    combs = [
        # Study convergence (changing just "nAng" and "prec") ...
        (2,  9, 5000,),
        (2, 17, 2500,),
        (2, 33, 1250,),

        # Study convergence (changing "cons", "nAng" and "prec") ...
        # (2,  9, 5000,),
        # (4, 17, 2500,),
        # (8, 33, 1250,),

        # With "nAng=17" and "prec=2500", is "cons=2" good enough?
        # (2, 17, 2500,),
        # (4, 17, 2500,),

        # With "nAng=33" and "prec=1250", is "cons=2" good enough?
        # (2, 33, 1250,),
        # (8, 33, 1250,),
    ]

    # Load colour tables ...
    with open(f"{pyguymer3.__path__[0]}/data/json/colourTables.json", "rt", encoding = "utf-8") as fObj:
        cts = json.load(fObj)

    # **************************************************************************

    # Loop over combinations ...
    for cons, nAng, prec in combs:
        # Create short-hands ...
        # NOTE: Say that 40,000 metres takes 1 hour at 20 knots.
        freqLand = 24 * 40000 // prec                                           # [#]
        freqSimp = 40000 // prec                                                # [#]

        # Populate GST command ...
        cmd = [
            "python3.12", "run.py",
            "0.0", "0.0", "20.0",               # dummy values
            "--conservatism", f"{cons:.1f}",    # LOOP VARIABLE
            "--duration", "0.01",               # dummy value
            "--freqLand", f"{freqLand:d}",      # ~daily land re-evaluation
            "--freqSimp", f"{freqSimp:d}",      # ~hourly simplification
            "--nAng", f"{nAng:d}",              # LOOP VARIABLE
            "--precision", f"{prec:.1f}",       # LOOP VARIABLE
            "--resolution", res,
        ]
        if args.debug:
            cmd.append("--debug")

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

    # Define axes for initial image ...
    dLon = 10.0                                                                 # [°]
    dLat = 10.0                                                                 # [°]
    nLon = 36                                                                   # [px]
    nLat = 18                                                                   # [px]

    # Define scale for final upscaled image ...
    scale = 100

    # Loop over combinations ...
    for cons, nAng, prec in combs:
        # Deduce directory name ...
        dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/local=F_nAng={nAng:d}_prec={prec:.2e}"

        # Deduce file name and skip if it is missing ...
        fname = f"{dname}/allLands.wkb.gz"
        if not os.path.exists(fname):
            continue

        print(f"Surveying \"{fname}\" ...")

        # **********************************************************************

        # Initialize array ...
        hist = numpy.zeros((nLat, nLon), dtype = numpy.uint64)                  # [#]

        # Load [Multi]Polygon ...
        with gzip.open(fname, mode = "rb") as gzObj:
            allLands = shapely.wkb.loads(gzObj.read())

        # Loop over Polygons ...
        for allLand in pyguymer3.geo.extract_polys(allLands, onlyValid = False, repair = False):
            # Loop over coordinates in the exterior ring ...
            for coord in allLand.exterior.coords:
                # Find the pixel that this coordinate corresponds to ...
                iLon = max(0, min(nLon - 1, math.floor((coord[0] + 180.0) / dLon))) # [px]
                iLat = max(0, min(nLat - 1, math.floor(( 90.0 - coord[1]) / dLat))) # [px]

                # Increment array ...
                hist[iLat, iLon] += 1                                           # [#]

        print(f" > Maximum value = {hist.max():,d}.")

        # **********************************************************************

        # NOTE: Maximum value = 2,148.
        # NOTE: Maximum value = 3,548.
        # NOTE: Maximum value = 5,860.

        # **********************************************************************

        # Initialize array ...
        histImg = numpy.zeros((nLat * scale, nLon * scale, 3), dtype = numpy.uint8)

        # Loop over initial longitudes ...
        for iLon0 in range(nLon):
            # Deduce final upscaled indices ...
            iLon1 =  iLon0      * scale                                         # [px]
            iLon2 = (iLon0 + 1) * scale                                         # [px]

            # Loop over initial latitudes ...
            for iLat0 in range(nLat):
                # Deduce final upscaled indices ...
                iLat1 =  iLat0      * scale                                     # [px]
                iLat2 = (iLat0 + 1) * scale                                     # [px]

                # Populate array ...
                for iLon in range(iLon1, iLon2):
                    for iLat in range(iLat1, iLat2):
                        if hist[iLat0, iLon0] > 0:
                            color = round(
                                min(
                                    255.0,
                                    255.0 * hist[iLat0, iLon0].astype(numpy.float64) / 5860.0,
                                )
                            )
                            histImg[iLat, iLon, :] = cts["rainbow"][color][:]
                        else:
                            histImg[iLat, iLon, :] = 255

        # Convert array to image ...
        histImg = PIL.Image.fromarray(histImg)

        # **********************************************************************

        # Create drawing object ...
        histDraw = PIL.ImageDraw.Draw(histImg)

        # Loop over Polygons ...
        for allLand in pyguymer3.geo.extract_polys(allLands, onlyValid = False, repair = False):
            # Initialize list ...
            coords = []                                                         # [px], [px]

            # Loop over coordinates in exterior ring ...
            for coord in allLand.exterior.coords:
                # Deduce location and append to list ...
                x = max(0.0, min(float(nLon * scale), float(scale) * (coord[0] + 180.0) / dLon))    # [px]
                y = max(0.0, min(float(nLat * scale), float(scale) * ( 90.0 - coord[1]) / dLat))    # [px]
                coords.append((x, y))                                           # [px], [px]

            # Draw exterior ring ...
            histDraw.line(coords, fill = (255, 255, 255), width = 1)

        # **********************************************************************

        print(f"Saving \"complexity_res={res}_cons={cons:.2e}_nAng={nAng:d}_prec={prec:.2e}.png\" ...")

        # Save PNG ...
        histImg.save(f"complexity_res={res}_cons={cons:.2e}_nAng={nAng:d}_prec={prec:.2e}.png")
        pyguymer3.image.optimize_image(f"complexity_res={res}_cons={cons:.2e}_nAng={nAng:d}_prec={prec:.2e}.png", strip = True)
