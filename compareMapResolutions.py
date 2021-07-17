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

# Import my modules ...
try:
    import pyguymer3
    import pyguymer3.geo
    import pyguymer3.image
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# ******************************************************************************

# Define starting location ...
lon = -1.0                                                                      # [°]
lat = 50.7                                                                      # [°]

# Define extent ...
ext = [lon - 1.0, lon + 1.0, lat - 1.0, lat + 1.0]                              # [°], [°], [°], [°]

# ******************************************************************************

# Define resolutions and their colours ...
pairs = [
    ("110m", (1.0, 0.0, 0.0, 0.5)),
    ( "50m", (0.0, 1.0, 0.0, 0.5)),
    ( "10m", (0.0, 0.0, 1.0, 0.5)),
]

# ******************************************************************************

# Create figure ...
fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = 300)

# Create axis and make it pretty ...
ax = fg.add_subplot(projection = cartopy.crs.Orthographic(central_longitude = lon, central_latitude = lat))
ax.set_extent(ext)
pyguymer3.geo.add_map_background(ax, name = "shaded-relief", resolution = "large4096px")
pyguymer3.geo.add_horizontal_gridlines(ax, ext, ny = 21)
pyguymer3.geo.add_vertical_gridlines(ax, ext, nx = 21)

# Loop over resolutions ...
for i, (resolution, colour) in enumerate(pairs):
    # Deduce Shapefile name ...
    sfile = cartopy.io.shapereader.natural_earth(resolution = resolution, category = "physical", name = "land")

    print(f"Loading \"{sfile}\" ...")

    # Initialize list ...
    polys = []

    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(sfile).records():
        # Skip bad records ...
        if not record.geometry.is_valid:
            print(f"WARNING: Skipping a piece of land in \"{sfile}\" as it is not valid.")
            continue
        if record.geometry.is_empty:
            print(f"WARNING: Skipping a piece of land in \"{sfile}\" as it is empty.")
            continue

        # Loop over all the bad Natural Earth Polygons in this geometry ...
        for badPoly in pyguymer3.geo.extract_polys(record.geometry):
            # Add the individual good Polygons that make up this bad Natural
            # Earth Polygon to the list ...
            polys += pyguymer3.geo.extract_polys(pyguymer3.geo.remap(badPoly))

    # Plot Polygons ...
    ax.add_geometries(
        polys,
        cartopy.crs.PlateCarree(),
        edgecolor = (0.0, 0.0, 0.0, 0.5),
        facecolor = colour,
        linewidth = 1.0
    )

    # Clean up ...
    del polys

# Save figure ...
fg.savefig("compareMapResolutions.png", bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
matplotlib.pyplot.close(fg)

# Optimize PNG ...
pyguymer3.image.optimize_image("compareMapResolutions.png", strip = True)
