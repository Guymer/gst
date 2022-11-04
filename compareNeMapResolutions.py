#!/usr/bin/env python3

# Import standard modules ...
import os

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
try:
    import shapely
except:
    raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

# Import my modules ...
try:
    import pyguymer3
    import pyguymer3.geo
    import pyguymer3.image
    import pyguymer3.media
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# ******************************************************************************

# Define central location ...
lon = -1.0                                                                      # [°]
lat = 50.5                                                                      # [°]

# Define resolutions ...
ress = [
    "110m",
     "50m",
     "10m",
]

# ******************************************************************************

# Find how large a 100km radius circle is around the central location ...
point = shapely.geometry.point.Point(lon, lat)
poly = pyguymer3.geo.buffer(
    point,
    100.0e3,
    fill = -1.0,
    nang = 9,
    simp = -1.0,
)

# Create extent ...
ext = [
    poly.bounds[0],                     # minx
    poly.bounds[2],                     # maxx
    poly.bounds[1],                     # miny
    poly.bounds[3],                     # maxy
]                                                                               # [°]

# Clean up ...
del point, poly

# ******************************************************************************

# Initialize list ...
frames = []

# Loop over resolutions ...
for res in ress:
    # Deduce PNG name, append it to the list and skip if it already exists ...
    frame = f"compareNeMapResolutions_res={res}.png"
    frames.append(frame)
    if os.path.exists(frame):
        continue

    print(f"Making \"{frame}\" ...")

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
        locs = range(-90, 91, 1),
    )
    pyguymer3.geo.add_vertical_gridlines(
        ax,
        ext,
        locs = range(-180, 181, 1),
    )

    # Deduce Shapefile name ...
    sfile = cartopy.io.shapereader.natural_earth(
          category = "physical",
              name = "land",
        resolution = res,
    )

    print(f" > Loading \"{sfile}\" ...")

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
        edgecolor = (1.0, 0.0, 0.0, 1.0),
        facecolor = (1.0, 0.0, 0.0, 0.5),
        linewidth = 1.0,
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
    fg.suptitle(f"res={res}")
    fg.tight_layout()

    # Save figure ...
    fg.savefig(
        frame,
               dpi = 300,
        pad_inches = 0.1,
    )
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image(frame, strip = True)

# ******************************************************************************

print("Making \"compareNeMapResolutions.webp\" ...")

# Save 1fps WEBP ...
pyguymer3.media.images2webp(
    frames,
    "compareNeMapResolutions.webp",
      fps = 1.0,
    strip = True,
)

# Set maximum sizes ...
# NOTE: By inspection, the PNG frames are 2700px tall.
maxSizes = [256, 512, 1024, 2048]                                               # [px]

# Loop over maximum sizes ...
for maxSize in maxSizes:
    print(f"Making \"compareNeMapResolutions{maxSize:04d}px.webp\" ...")

    # Save 1fps WEBP ...
    pyguymer3.media.images2webp(
        frames,
        f"compareNeMapResolutions{maxSize:04d}px.webp",
                 fps = 1.0,
        screenHeight = maxSize,
         screenWidth = maxSize,
               strip = True,
    )
