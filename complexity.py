#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.10/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
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

    # Load colour tables ...
    with open(f"{pyguymer3.__path__[0]}/data/json/colourTables.json", "rt", encoding = "utf-8") as fObj:
        cts = json.load(fObj)

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

    # Define axes for initial image ...
    dLon = 10.0                                                                 # [°]
    dLat = 10.0                                                                 # [°]
    nLon = 36                                                                   # [px]
    nLat = 18                                                                   # [px]

    # Define scale for final upscaled image ...
    scale = 100

    # Loop over combinations ...
    for cons, nang, prec in combs:
        # Deduce directory name ...
        dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/nang={nang:d}_prec={prec:.2e}"

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

        # Clean up ...
        del hist

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

            # Clean up ...
            del coords

        # Clean up ...
        del histDraw

        # **********************************************************************

        print(f"Saving \"complexity_res={res}_cons={cons:.2e}_nang={nang:d}_prec={prec:.2e}.png\" ...")

        # Save PNG ...
        histImg.save(f"complexity_res={res}_cons={cons:.2e}_nang={nang:d}_prec={prec:.2e}.png")
        pyguymer3.image.optimize_image(f"complexity_res={res}_cons={cons:.2e}_nang={nang:d}_prec={prec:.2e}.png", strip = True)

        # Clean up ...
        del histImg
