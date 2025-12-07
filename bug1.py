#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse

    # Import special modules ...
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                            "backend" : "Agg",                                  # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
                         "figure.dpi" : 300,
                     "figure.figsize" : (9.6, 7.2),                             # NOTE: See https://github.com/Guymer/misc/blob/main/README.md#matplotlib-figure-sizes
                          "font.size" : 8,
                "image.interpolation" : "none",
                     "image.resample" : False,
            }
        )
        import matplotlib.pyplot
    except:
        raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
    try:
        import numpy
    except:
        raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
    try:
        import shapely
        import shapely.geometry
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
            description = "Demonstrate a bug.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action = "store_true",
          dest = "debug",
          help = "print debug messages",
    )
    parser.add_argument(
        "--timeout",
        default = 60.0,
           help = "the timeout for any requests/subprocess calls (in seconds)",
           type = float,
    )
    args = parser.parse_args()

    # **************************************************************************

    # Configure functions ...
    nAng = 361                                                                  # [#]
    simp = 0.001                                                                # [°]

    # Define starting location and the four buffering distances ...
    # lon = 1.0                                                                   # [°]
    # lat = 50.5                                                                  # [°]
    # maxDists = [4382, 4383, 4384, 4385]                                         # [km]

    # Define starting location and the four buffering distances ...
    # lon = -1.0                                                                  # [°]
    # lat = 50.5                                                                  # [°]
    # maxDists = [4382, 4383, 4384, 4385]                                         # [km]

    # Define starting location and the four buffering distances ...
    # lon = 1.0                                                                   # [°]
    # lat = -50.5                                                                 # [°]
    # maxDists = [4382, 4383, 4384, 4385]                                         # [km]

    # Define starting location and the four buffering distances ...
    # lon = -1.0                                                                  # [°]
    # lat = -50.5                                                                 # [°]
    # maxDists = [4382, 4383, 4384, 4385]                                         # [km]

    # Define starting location and the four buffering distances ...
    lon = 170.0                                                                 # [°]
    lat = 10.0                                                                  # [°]
    maxDists = [2000, 3000, 4000, 5000]                                         # [km]

    # Create the ship ...
    ship = shapely.geometry.point.Point(lon, lat)

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (12.8, 7.2))

    # Create axes ...
    ax = fg.subplots(2, 2).flatten()

    # Loop over distances ...
    for i, maxDist in enumerate(maxDists):
        print(f"Distance {i + 1:d} is {maxDist:,d} km ...")

        # Sail the ship in one go ...
        maxShip1 = pyguymer3.geo.buffer(
            ship,
            float(maxDist) * 1000.0,
            debug = args.debug,
             nAng = nAng,
             simp = simp,
        )

        # Manually plot the exterior rings of all of the Polygons ...
        for j, poly in enumerate(pyguymer3.geo.extract_polys(maxShip1, onlyValid = False, repair = False)):
            coords = numpy.array(poly.exterior.coords)                          # [°]
            ax[i].plot(
                coords[:, 0],
                coords[:, 1],
                color = f"C{j:d}",
            )

        # Sail the ship in four goes ...
        maxShip2 = pyguymer3.geo.buffer(
            pyguymer3.geo.buffer(
                pyguymer3.geo.buffer(
                    pyguymer3.geo.buffer(
                        ship,
                        0.25 * float(maxDist) * 1000.0,
                        debug = args.debug,
                         nAng = nAng,
                         simp = simp,
                    ),
                    0.25 * float(maxDist) * 1000.0,
                    debug = args.debug,
                     nAng = nAng,
                     simp = simp,
                ),
                0.25 * float(maxDist) * 1000.0,
                debug = args.debug,
                 nAng = nAng,
                 simp = simp,
            ),
            0.25 * float(maxDist) * 1000.0,
            debug = args.debug,
             nAng = nAng,
             simp = simp,
        )

        # Manually plot the exterior rings of all of the Polygons ...
        for j, poly in enumerate(pyguymer3.geo.extract_polys(maxShip2, onlyValid = False, repair = False)):
            coords = numpy.array(poly.exterior.coords)                          # [°]
            ax[i].plot(
                coords[:, 0],
                coords[:, 1],
                    color = f"C{j:d}",
                linestyle = "--",
            )

        # Plot the starting location ...
        ax[i].scatter(
            [lon],
            [lat],
             color = "gold",
            marker = "*",
        )

        # Configure axis ...
        ax[i].grid()
        ax[i].set_aspect("equal")
        ax[i].set_xlabel("Longitude [°]")
        ax[i].set_xlim(-180.5, +180.5)
        ax[i].set_xticks(range(-180, 225, 45))
        ax[i].set_ylabel("Latitude [°]")
        ax[i].set_ylim(-90.5, +90.5)
        ax[i].set_yticks(range(-90, 135, 45))

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("bug1.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimise_image(
        "bug1.png",
          debug = args.debug,
          strip = True,
        timeout = args.timeout,
    )
