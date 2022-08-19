#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.10/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse

    # Import my modules ...
    import funcs

    # Create argument parser and parse the arguments ...
    parser = argparse.ArgumentParser(allow_abbrev = False, description = "This script reads in a starting coordinate and a sailing speed and then calculates the maximum possible sailing distance on the surface of the Earth that the vessel can reach in the specified time.")
    parser.add_argument("lon", help = "the longitude of the starting point (in degrees)", type = float)
    parser.add_argument("lat", help = "the latitude of the starting point (in degrees)", type = float)
    parser.add_argument("spd", help = "the speed of the vessel (in knots)", type = float)
    parser.add_argument("--detailed", action = "store_true", help = "take account of minor islands")
    parser.add_argument("--dur", default = 1.0, help = "the duration of the voyage (in days)", type = float)
    parser.add_argument("--freqFillSimp", default = 25, help = "fill in and simplify the sailing contour every freqFillSimp iteration", type = int)
    parser.add_argument("--freqLand", default = 100, help = "re-evaluate the relevant land every freqLand iteration", type = int)
    parser.add_argument("--freqPlot", default = 50, help = "plot sailing contours every freqPlot iteration", type = int)
    parser.add_argument("--local", action = "store_true", help = "the plot has only local extent")
    parser.add_argument("--nang", default = 10, help = "the number of directions from each point that the vessel could sail in", type = int)
    parser.add_argument("--plot", action = "store_true", help = "make a plot")
    parser.add_argument("--prec", default = 1000.0, help = "the precision of the calculation (in metres)", type = float)
    parser.add_argument("--res", default = "110m", help = "the resolution of the Natural Earth datasets", type = str)
    parser.add_argument("--tol", default = 1.0e-10, help = "the Euclidean distance that defines two points as being the same (in degrees)", type = float)
    args = parser.parse_args()

    # Sail the vessel ...
    funcs.sail(
        args.lon,
        args.lat,
        args.spd,
        detailed = args.detailed,
        dur = args.dur,
        freqFillSimp = args.freqFillSimp,
        freqLand = args.freqLand,
        freqPlot = args.freqPlot,
        local = args.local,
        nang = args.nang,
        plot = args.plot,
        prec = args.prec,
        res = args.res,
        tol = args.tol
    )
