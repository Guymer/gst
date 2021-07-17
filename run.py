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
    dur = 0.1                                                                   # [days]

    # **************************************************************************

    # Loop over number of angles ...
    for nang in [10, 19, 37, 91, 181, 361]:
        print(f"Running with {360 // (nang - 1):d}° wedges ...")

        # Loop over Natural Earth resolutions ...
        for res in ["110m", "50m", "10m"]:
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
