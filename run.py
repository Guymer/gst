#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: https://docs.python.org/3.8/library/multiprocessing.html#multiprocessing-programming
if __name__ == "__main__":
    # Import my modules ...
    import funcs

    # Define starting location (just outside Portsmouth Harbour), sailing speed
    # (of an average vessel) and sailing duration ...
    lon = -1.0                                                                  # [°]
    lat = 50.7                                                                  # [°]
    spd = 20.0                                                                  # [kts]
    dur = 0.2                                                                   # [days]

    # Set run mode ...
    debug = True

    # **************************************************************************

    # Configure calculation based off run mode ...
    if debug:
        nang = 37
        res = "110m"
    else:
        nang = 361
        res = "50m"

    # **************************************************************************

    # Sail the vessel (ignoring minor islands) ...
    funcs.sail(
        lon,
        lat,
        spd,
        detailed = False,
        dur = dur,
        freqFillSimp = 25,
        freqLand = 100,
        freqPlot = 50,
        local = True,
        nang = nang,
        res = res
    )
