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

    # Sail the vessel (ignoring minor islands, sailing in steps lasting 12
    # minutes and only plotting contours every 6 hours for 2 days in the local
    # vacinity) ...
    funcs.sail(lon, lat, spd, detailed = False, local = True, nth = 30, ntot = 240)
