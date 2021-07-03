#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: https://docs.python.org/3.8/library/multiprocessing.html#multiprocessing-programming
if __name__ == "__main__":
    # Import my modules ...
    import funcs

    # Define starting location (just outside Portsmouth Harbour), sailing
    # speed (of an average vessel) and sailing duration ...
    lat = 50.774438                                                             # [°]
    lon = -1.108652                                                             # [°]
    spd = 20.0                                                                  # [kts]
    dur = 0.01                                                                  # [days]

    # Set run mode ...
    debug = False

    # **************************************************************************

    # Configure calculation based off run mode ...
    if debug:
        res = "110m"
        nang = 37
        prec = 10000.0                                                          # [m]
    else:
        res = "10m"
        nang = 361
        prec = 100.0                                                            # [m]

    # **************************************************************************

    # Sail the vessel (ignoring minor islands) ...
    funcs.sail(
        lon,
        lat,
        spd,
        debug = debug,
        detailed = False,
        dur = dur,
        local = True,
        nang = nang,
        nth = 5,
        prec = prec,
        res = res
    )
