#!/usr/bin/env python3

# Import standard modules ...
import gzip
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
except:
    raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
try:
    import shapely
    import shapely.wkb
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

# ******************************************************************************

# Initialize global bounding box ...
xmin = +180.0                                                                   # [°]
ymin =  +90.0                                                                   # [°]
xmax = -180.0                                                                   # [°]
ymax =  -90.0                                                                   # [°]

# Loop over number of angles ...
for nang in [10, 19, 37, 91, 181, 361]:
    # Loop over distances ...
    for dist in range(8):
        # Deduce file name and skip if it is missing ...
        fname = f"detailed=F_nang={nang:d}_prec=1.00e+02_res=10m_simp=8.99e-05_tol=1.00e-10/freqFillSimp=25_freqLand=100_lat=+50.700000_lon=-001.000000/contours/istep=00{dist:02d}99.wkb.gz"
        if not os.path.exists(fname):
            continue

        print(f"Plotting \"{fname}\" ...")

        # Load Polygon ...
        ship = shapely.wkb.loads(gzip.open(fname, "rb").read())

        # Update global bounding box ...
        xmin = min(xmin, ship.bounds[0])                                        # [°]
        ymin = min(ymin, ship.bounds[1])                                        # [°]
        xmax = max(xmax, ship.bounds[2])                                        # [°]
        ymax = max(ymax, ship.bounds[3])                                        # [°]

        # Clean up ...
        del ship

# Define extent ...
ext = [xmin - 0.05, xmax + 0.05, ymin - 0.05, ymax + 0.05]                      # [°], [°], [°], [°]

# ******************************************************************************

# Create figure ...
fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = 300)
ax = fg.add_subplot(projection = cartopy.crs.Orthographic(central_longitude = lon, central_latitude = lat))

# Configure axis ...
ax.set_extent(ext)
pyguymer3.geo.add_map_background(ax, resolution = "large4096px")
pyguymer3.geo.add_horizontal_gridlines(ax, ext, locs = [50.0, 50.5, 51.0])
pyguymer3.geo.add_vertical_gridlines(ax, ext, locs = [-2.0, -1.5, -1.0, -0.5, 0.0])

# ******************************************************************************

# Load MultiPolygon ...
allLands = shapely.wkb.loads(gzip.open("detailed=F_nang=10_prec=1.00e+02_res=10m_simp=8.99e-05_tol=1.00e-10/allLands.wkb.gz", "rb").read())

# Plot MultiPolygon ...
ax.add_geometries(
    allLands,
    cartopy.crs.PlateCarree(),
    edgecolor = (1.0, 0.0, 0.0, 1.0),
    facecolor = (1.0, 0.0, 0.0, 0.5),
    linewidth = 1.0
)

# Clean up ...
del allLands

# ******************************************************************************

# Initialize lists ...
labels = []
lines = []

# Loop over number of angles (and their colours) ...
for nang, color in [(10, "C0"), (19, "C1"), (37, "C2"), (91, "C3"), (181, "C4"), (361, "C5")]:
    # Loop over distances ...
    for dist in range(1, 9):
        # Deduce file name and skip if it is missing ...
        fname = f"detailed=F_nang={nang:d}_prec=1.00e+02_res=10m_simp=8.99e-05_tol=1.00e-10/freqFillSimp=25_freqLand=100_lat=+50.700000_lon=-001.000000/contours/istep=00{dist:02d}00.wkb.gz"
        if not os.path.exists(fname):
            continue

        # Load Polygon ...
        ship = shapely.wkb.loads(gzip.open(fname, "rb").read())

        # Plot Polygon ...
        ax.add_geometries(
            [ship],
            cartopy.crs.PlateCarree(),
            edgecolor = color,
            facecolor = "none",
            linewidth = 1.0
        )

        # Check if it is the first distance for this number of angles ...
        if dist == 1:
            # Add an entry to the legend ...
            labels.append(f"{nang:d} Angles")
            lines.append(matplotlib.lines.Line2D([], [], color = color))

        # Clean up ...
        del ship

# ******************************************************************************

# Configure axis ...
ax.legend(
    lines,
    labels,
    fontsize = "small",
    loc = "upper center",
    ncol = 3
)

# Save figure ...
fg.savefig("compareBufferResolutions.png", bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
matplotlib.pyplot.close(fg)

# Optimize PNG ...
pyguymer3.image.optimize_image("compareBufferResolutions.png", strip = True)
