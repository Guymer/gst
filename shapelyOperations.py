#!/usr/bin/env python3

# Import special modules ...
try:
    import cartopy
except:
    raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
try:
    import matplotlib
    matplotlib.use("Agg")                                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
    import matplotlib.pyplot
except:
    raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
try:
    import numpy
except:
    raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
try:
    import shapely
except:
    raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

# Import my modules ...
try:
    import pyguymer3
    import pyguymer3.geo
    import pyguymer3.image
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# Define starting location ...
lon = -1.0                                                                      # [°]
lat = 50.7                                                                      # [°]

# Define extent ...
ext = [lon - 5.0, lon + 5.0, lat - 5.0, lat + 5.0]                              # [°], [°], [°], [°]

# ******************************************************************************

# Create figure ...
fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = 300)
ax = fg.add_subplot(projection = cartopy.crs.Orthographic(central_longitude = lon, central_latitude = lat))

# Configure axis ...
ax.set_extent(ext)
pyguymer3.geo.add_map_background(ax, resolution = "large8192px")
pyguymer3.geo.add_horizontal_gridlines(ax, ext, locs = [45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56])
pyguymer3.geo.add_vertical_gridlines(ax, ext, locs = [-6, -5, -4, -3, -2, -1, 0, +1, +2, +3, +4])

# ******************************************************************************

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
    linewidth = 1.0
)

# ******************************************************************************

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
    linewidth = 1.0
)

# ******************************************************************************

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
    linewidth = 1.0
)

# ******************************************************************************

# Find the limit of the ship's sailing distance and plot it ...
limit = ship.exterior
print(type(limit))
coords = numpy.array(limit.coords)                                              # [°]
ax.plot(
    coords[:, 0],
    coords[:, 1],
    color = "C0",
    linewidth = 1.0,
    marker = "d",
    transform = cartopy.crs.PlateCarree()
)

# Find the limit of the ship's sailing distance that is not on the coastline of
# the first island and plot it ...
limit = limit.difference(land1)
print(type(limit))
coords = numpy.array(limit.coords)                                              # [°]
ax.plot(
    coords[:, 0],
    coords[:, 1],
    color = "C1",
    linewidth = 1.0,
    marker = "d",
    transform = cartopy.crs.PlateCarree()
)

# Find the limit of the ship's sailing distance that is not on either the
# coastline of the first island or the coastline of the second island and plot
# it ...
limit = limit.difference(land2)
print(type(limit))
for thing in limit:
    coords = numpy.array(thing.coords)                                          # [°]
    ax.plot(
        coords[:, 0],
        coords[:, 1],
        color = "C2",
        linewidth = 1.0,
        marker = "d",
        transform = cartopy.crs.PlateCarree()
    )

# ******************************************************************************

# Save figure ...
fg.savefig("shapelyOperations.png", bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
matplotlib.pyplot.close(fg)

# Optimize PNG ...
pyguymer3.image.optimize_image("shapelyOperations.png", strip = True)
