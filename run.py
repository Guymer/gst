#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: https://docs.python.org/3.8/library/multiprocessing.html#multiprocessing-programming
if __name__ == "__main__":
    # Import my modules ...
    import funcs

    # Define starting location (just outside Portsmouth Harbour) and sailing
    # speed (of an average vessel) ...
    lat = 50.774438                                                             # [°]
    lon = -1.108652                                                             # [°]
    spd = 20.0                                                                  # [kts]

    # Set run mode ...
    debug = False

    # **************************************************************************

    # Configure calculation based off run mode ...
    if debug:
        res = "110m"
        nang = 37
        simp = 0.1
    else:
        res = "10m"
        nang = 361
        simp = 0.0001

    # **************************************************************************

    # Sail the vessel (ignoring minor islands, sailing in steps lasting 1 minute
    # and 12 seconds and only plotting contours every 6 minutes for 3 hours in
    # the local vacinity) ...
    funcs.sail(lon, lat, spd, debug = debug, detailed = False, dur = 0.02, local = True, nang = nang, nth = 5, ntot = 150, res = res, simp = simp)
