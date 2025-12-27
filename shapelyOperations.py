#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import pathlib

    # Import special modules ...
    try:
        import cartopy
        cartopy.config.update(
            {
                "cache_dir" : pathlib.PosixPath("~/.local/share/cartopy").expanduser(),
            }
        )
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
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
            description = "Demonstrate some Shapely operations on some shapes.",
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

    # Define central location ...
    lon = -1.0                                                                  # [°]
    lat = 50.5                                                                  # [°]

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

    # Create axis ...
    ax = pyguymer3.geo.add_axis(
        fg,
        debug = args.debug,
         dist = 500.0e3,
          lat = lat,
          lon = lon,
    )

    # Configure axis ...
    pyguymer3.geo.add_map_background(
        ax,
             debug = args.debug,
              name = "shaded-relief",
        resolution = "large8192px",
    )

    # **************************************************************************

    # Make an island ...
    land1 = shapely.geometry.polygon.Polygon(
        [
            (-2.0, +53.0),
            (-2.0, +51.0),
            ( 0.0, +51.0),
            ( 0.0, +53.0),
            (-2.0, +53.0),
        ]
    )
    ax.add_geometries(
        [land1],
        cartopy.crs.PlateCarree(),
        edgecolor = (1.0, 0.0, 0.0, 0.50),
        facecolor = (1.0, 0.0, 0.0, 0.25),
        linewidth = 1.0,
    )

    # **************************************************************************

    # Make an island ...
    land2 = shapely.geometry.polygon.Polygon(
        [
            ( 0.0, +50.0),
            ( 0.0, +48.0),
            (+2.0, +48.0),
            (+2.0, +50.0),
            ( 0.0, +50.0),
        ]
    )
    ax.add_geometries(
        [land2],
        cartopy.crs.PlateCarree(),
        edgecolor = (0.0, 1.0, 0.0, 0.50),
        facecolor = (0.0, 1.0, 0.0, 0.25),
        linewidth = 1.0,
    )

    # **************************************************************************

    # Make a ship ...
    ship = shapely.geometry.polygon.Polygon(
        [
            (-1.0, +51.0),
            (-1.0, +49.0),
            (+1.0, +49.0),
            (+1.0, +51.0),
            (-1.0, +51.0),
        ]
    )
    ax.add_geometries(
        [ship],
        cartopy.crs.PlateCarree(),
        edgecolor = (0.0, 0.0, 1.0, 0.50),
        facecolor = (0.0, 0.0, 1.0, 0.25),
        linewidth = 1.0,
    )

    # **************************************************************************

    # Find the limit of the ship's sailing distance and plot it ...
    limit = ship.exterior
    print(type(limit))
    coords = numpy.array(limit.coords)                                          # [°]
    ax.plot(
        coords[:, 0],
        coords[:, 1],
            color = "C0",
        linewidth = 1.0,
           marker = "d",
        transform = cartopy.crs.PlateCarree(),
    )

    # Find the limit of the ship's sailing distance that is not on the coastline
    # of the first island and plot it ...
    limit = limit.difference(land1)
    print(type(limit))
    coords = numpy.array(limit.coords)                                          # [°]
    ax.plot(
        coords[:, 0],
        coords[:, 1],
            color = "C1",
        linewidth = 1.0,
           marker = "d",
        transform = cartopy.crs.PlateCarree(),
    )

    # Find the limit of the ship's sailing distance that is not on either the
    # coastline of the first island or the coastline of the second island and
    # plot it ...
    limit = limit.difference(land2)
    print(type(limit))
    for line in pyguymer3.geo.extract_lines(limit, onlyValid = False):
        coords = numpy.array(line.coords)                                       # [°]
        ax.plot(
            coords[:, 0],
            coords[:, 1],
                color = "C2",
            linewidth = 1.0,
               marker = "d",
            transform = cartopy.crs.PlateCarree(),
        )

    # **************************************************************************

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("shapelyOperations.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimise_image(
        "shapelyOperations.png",
          debug = args.debug,
          strip = True,
        timeout = args.timeout,
    )
