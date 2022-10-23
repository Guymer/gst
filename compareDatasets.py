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
    matplotlib.pyplot.rcParams.update({"font.size" : 8})
except:
    raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None

# Import my modules ...
try:
    import pyguymer3
    import pyguymer3.geo
    import pyguymer3.image
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# ******************************************************************************

# Define central location ...
lon = -1.0                                                                      # [°]
lat = 50.5                                                                      # [°]

# Define extent ...
ext = [
    lon - 1.0,
    lon + 1.0,
    lat - 1.0,
    lat + 1.0,
]                                                                               # [°]

# Set mode ...
debug = True

# Set tolerance ...
tol = 1.0e-10

# ******************************************************************************

# Set Global Self-Consistent Hierarchical High-Resolution Geography Shapefile
# list ...
# NOTE: See https://www.ngdc.noaa.gov/mgg/shorelines/
gshhgShapeFiles = [
    cartopy.io.shapereader.gshhs(
        level = 1,
        scale = "f",
    ),
]

# Set Natural Earth Shapefile list ...
# NOTE: See https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/
# NOTE: See https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-minor-islands/
neShapeFiles = [
    cartopy.io.shapereader.natural_earth(
          category = "physical",
              name = "land",
        resolution = "10m",
    ),
    cartopy.io.shapereader.natural_earth(
          category = "physical",
              name = "minor_islands",
        resolution = "10m",
    ),
]

# ******************************************************************************

# Create figure ...
fg = matplotlib.pyplot.figure(
        dpi = 300,
    figsize = (9, 6),
)

# Create axis ...
ax = fg.add_subplot(
    projection = cartopy.crs.Orthographic(
        central_longitude = lon,
         central_latitude = lat,
    )
)

# Configure axis ...
ax.set_extent(ext)
pyguymer3.geo.add_map_background(
    ax,
          name = "shaded-relief",
    resolution = "large8192px",
)
pyguymer3.geo.add_horizontal_gridlines(
    ax,
    ext,
    ngrid = 21,
)
pyguymer3.geo.add_vertical_gridlines(
    ax,
    ext,
    ngrid = 21,
)

# Loop over Global Self-Consistent Hierarchical High-Resolution Geography
# Shapefiles ...
for sfile in gshhgShapeFiles:
    print(f"Loading \"{sfile}\" ...")

    # Initialize list ...
    polys = []

    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(sfile).records():
        # Add the Polygons to the list ...
        polys += pyguymer3.geo.extract_polys(record.geometry)

    # Plot Polygons ...
    ax.add_geometries(
        polys,
        cartopy.crs.PlateCarree(),
        edgecolor = (0.0, 0.0, 0.0, 0.5),
        facecolor = (1.0, 0.0, 0.0, 0.5),
        linewidth = 1.0
    )

    # Clean up ...
    del polys

# Loop over Natural Earth Shapefiles ...
for sfile in neShapeFiles:
    print(f"Loading \"{sfile}\" ...")

    # Initialize list ...
    polys = []

    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(sfile).records():
        # Add the Polygons to the list ...
        polys += pyguymer3.geo.extract_polys(record.geometry)

    # Plot Polygons ...
    ax.add_geometries(
        polys,
        cartopy.crs.PlateCarree(),
        edgecolor = (0.0, 0.0, 0.0, 0.5),
        facecolor = (0.0, 0.0, 1.0, 0.5),
        linewidth = 1.0
    )

    # Clean up ...
    del polys

# Plot the central location ...
ax.scatter(
    [lon],
    [lat],
        color = "gold",
       marker = "*",
    transform = cartopy.crs.Geodetic(),
       zorder = 5.0,
)

# Configure figure ...
fg.tight_layout()

# Save figure ...
fg.savefig(
    "compareDatasets.png",
           dpi = 300,
    pad_inches = 0.1,
)
matplotlib.pyplot.close(fg)

# Optimize PNG ...
pyguymer3.image.optimize_image("compareDatasets.png", strip = True)
