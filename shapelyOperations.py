#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.11/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import os

    # Import special modules ...
    try:
        import cartopy
        cartopy.config.update(
            {
                "cache_dir" : os.path.expanduser("~/.local/share/cartopy_cache"),
            }
        )
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                       "backend" : "Agg",                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
                    "figure.dpi" : 300,
                "figure.figsize" : (9.6, 7.2),                                  # NOTE: See https://github.com/Guymer/misc/blob/main/README.md#matplotlib-figure-sizes
                     "font.size" : 8,
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
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # **************************************************************************

    # Define central location ...
    lon = -1.0                                                                  # [°]
    lat = 50.5                                                                  # [°]

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

    # Create axis ...
    ax = pyguymer3.geo.add_topDown_axis(
        fg,
        lon,
        lat,
        500.0e3,
    )

    # Configure axis ...
    pyguymer3.geo.add_map_background(
        ax,
              name = "shaded-relief",
        resolution = "large8192px",
    )
    pyguymer3.geo.add_horizontal_gridlines(
        ax,
        locs = range(-90, 91, 1),
    )
    pyguymer3.geo.add_vertical_gridlines(
        ax,
        locs = range(-180, 181, 1),
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
    pyguymer3.image.optimize_image("shapelyOperations.png", strip = True)
