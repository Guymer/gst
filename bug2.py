#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import gzip

    # Import special modules ...
    try:
        import shapely
        import shapely.wkb
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # **************************************************************************

    # Create argument parser and parse the arguments ...
    parser = argparse.ArgumentParser(
           allow_abbrev = False,
            description = "Demonstrate a bug.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action = "store_true",
          dest = "debug",
          help = "print debug messages",
    )
    args = parser.parse_args()

    # **************************************************************************

    # Deduce temporary file name ...
    tname = "res=i_cons=2.00e+00_tol=1.00e-10/local=F_nAng=33_prec=1.25e+03/freqLand=768_freqSimp=32_lon=-001.000000_lat=+50.500000/ship/istep=012287.wkb.gz"

    # Load [Multi]Polygon ...
    with gzip.open(tname, mode = "rb") as gzObj:
        ship = shapely.wkb.loads(gzObj.read())

    # Buffer the [Multi]Polygon ...
    maxShip = pyguymer3.geo.buffer(
        ship,
        1920000.0,
        debug = args.debug,
         fill = 1.0,
         nAng = 361,
         simp = -1.0,
          tol = 1.0e-10,
    )
