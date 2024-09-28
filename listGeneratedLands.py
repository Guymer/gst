#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import glob

    # **************************************************************************

    # Loop over all generated "allLands.wkb.gz" files ...
    for allLand in sorted(glob.glob("res=?_cons=?.??e???_tol=?.??e???/local=F_nang=*_prec=?.??e???/allLands.wkb.gz")):
        # Create short-hands ...
        partOne, partTwo, _ = allLand.split("/")
        res, cons, tol = partOne.split("_")
        local, nang, prec = partTwo.split("_")

        # Print combination ...
        print(f"{res}    {cons}    {tol}    {nang:8s}    {prec}")
