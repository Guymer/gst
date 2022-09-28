#!/usr/bin/env python3

# Import standard modules ...
import gzip
import os
import subprocess

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
lat = 50.5                                                                      # [°]

# ******************************************************************************

# Initialize global bounding box ...
xmin = +180.0                                                                   # [°]
ymin =  +90.0                                                                   # [°]
xmax = -180.0                                                                   # [°]
ymax =  -90.0                                                                   # [°]

# Loop over number of angles ...
for nang in [9, 17, 33, 65, 129, 257, 513]:
    print(f"Running \"--nang {nang:d}\" ...")

    # Run GST ...
    subprocess.run(
        [
            "python3.10", "run.py",
            f"{lon:+.1f}", f"{lat:+.1f}", "20.0",
            "--duration", "0.09",           # some sailing (20 knots * 0.09 days = 80.01 kilometres)
            "--precision", "1250.0",        # converged precision (from "compareBufferRadialResolutions.py")
            "--conservatism", "2.0",        # some conservatism
            "--freqLand", "768",            # ~daily land re-evaluation
            "--freqSimp", "768",            # ~daily simplification
            "--nang", f"{nang:d}",          # LOOP VARIABLE
            "--resolution", "10m",          # finest land resolution
        ],
           check = False,
        encoding = "utf-8",
          stderr = subprocess.DEVNULL,
          stdout = subprocess.DEVNULL,
    )

    # Loop over distances ...
    for dist in range(10, 90, 10):
        # Determine the step count ...
        istep = ((1000 * dist) // 1250) - 1

        # Deduce file name and skip if it is missing ...
        dname = f"detailed=F_res=10m_cons=2.00e+00_tol=1.00e-10/nang={nang:d}_prec=1.25e+03/freqLand=768_freqSimp=768_lon={lon:+011.6f}_lat={lat:+010.6f}/contours"
        fname = f"{dname}/istep={istep:06d}.wkb.gz"
        if not os.path.exists(fname):
            continue

        print(f"Surveying \"{fname}\" ...")

        # Load Polygon ...
        with gzip.open(fname, "rb") as fObj:
            ship = shapely.wkb.loads(fObj.read())

        # Update global bounding box ...
        xmin = min(xmin, ship.bounds[0])                                        # [°]
        ymin = min(ymin, ship.bounds[1])                                        # [°]
        xmax = max(xmax, ship.bounds[2])                                        # [°]
        ymax = max(ymax, ship.bounds[3])                                        # [°]

        # Clean up ...
        del ship

# Define extent ...
ext = [
    xmin - 0.05,
    xmax + 0.05,
    ymin - 0.05,
    ymax + 0.05,
]                                                                               # [°], [°], [°], [°]

# ******************************************************************************

# Create figure ...
fg = matplotlib.pyplot.figure(
        dpi = 300,
    figsize = (9, 12),
)

# Create axis ...
ax1 = fg.add_subplot(
    2,
    1,
    1,
    projection = cartopy.crs.Orthographic(
        central_longitude = lon,
         central_latitude = lat,
    ),
)

# Create axis ...
ax2 = fg.add_subplot(
    2,
    1,
    2,
)

# Configure axis ...
ax1.set_extent(ext)
pyguymer3.geo.add_map_background(ax1, resolution = "large8192px")
pyguymer3.geo.add_horizontal_gridlines(ax1, ext, locs = [50.0, 50.5, 51.0])
pyguymer3.geo.add_vertical_gridlines(ax1, ext, locs = [-2.0, -1.5, -1.0, -0.5, 0.0])

# Configure axis ...
ax2.grid()
ax2.set_xlabel("Number Of Angles")
ax2.set_ylabel("Area [%]")

# ******************************************************************************

# Load MultiPolygon ...
with gzip.open("detailed=F_res=10m_cons=2.00e+00_tol=1.00e-10/allLands.wkb.gz", "rb") as fObj:
    allLands = shapely.wkb.loads(fObj.read())

# Plot MultiPolygon ...
ax1.add_geometries(
    pyguymer3.geo.extract_polys(allLands),
    cartopy.crs.PlateCarree(),
    edgecolor = (1.0, 0.0, 0.0, 1.0),
    facecolor = (1.0, 0.0, 0.0, 0.5),
    linewidth = 1.0,
)

# Clean up ...
del allLands

# ******************************************************************************

# Initialize dictionary and list ...
data = {}
labels = []
lines = []

# Loop over number of angles ...
for iang, nang in enumerate([9, 17, 33, 65, 129, 257, 513]):
    # Create short-hand ...
    color = f"C{iang:d}"

    # Loop over distances ...
    for dist in range(10, 90, 10):
        # Determine the step count ...
        istep = ((1000 * dist) // 1250) - 1

        # Deduce file name and skip if it is missing ...
        dname = f"detailed=F_res=10m_cons=2.00e+00_tol=1.00e-10/nang={nang:d}_prec=1.25e+03/freqLand=768_freqSimp=768_lon={lon:+011.6f}_lat={lat:+010.6f}/contours"
        fname = f"{dname}/istep={istep:06d}.wkb.gz"
        if not os.path.exists(fname):
            continue

        print(f"Plotting \"{fname}\" ...")

        # Load Polygon ...
        with gzip.open(fname, "rb") as fObj:
            ship = shapely.wkb.loads(fObj.read())

        # Populate dictionary ...
        key = f"{dist:,d}km"
        if key not in data:
            data[key] = {
                "nang" : [],                                                    # [#]
                "area" : [],                                                    # [°2]
            }
        data[key]["nang"].append(nang)                                          # [#]
        data[key]["area"].append(ship.area)                                     # [°2]

        # Plot Polygon ...
        ax1.add_geometries(
            [ship],
            cartopy.crs.PlateCarree(),
            edgecolor = color,
            facecolor = "none",
            linewidth = 1.0,
        )

        # Check if it is the first distance for this number of angles ...
        if f"{nang:d} Angles" not in labels:
            # Add an entry to the legend ...
            labels.append(f"{nang:d} Angles")
            lines.append(matplotlib.lines.Line2D([], [], color = color))

        # Clean up ...
        del ship

# ******************************************************************************

# Loop over distances ...
for key in sorted(list(data.keys())):
    # Create short-hands ...
    nang = numpy.array(data[key]["nang"])                                       # [#]
    area = numpy.array(data[key]["area"])                                       # [°2]

    # Convert to ratio ...
    area /= area[-1]

    # Convert to percentage ...
    area *= 100.0                                                               # [%]

    # Plot data ...
    ax2.plot(
        nang,
        area,
         label = key,
        marker = "d",
    )

# ******************************************************************************

# Configure axis ...
ax1.legend(
    lines,
    labels,
    fontsize = "small",
         loc = "upper center",
        ncol = 3,
)

# Configure axis ...
ax2.axhspan(
    99,
    101,
    color = (0.0, 1.0, 0.0, 0.25),
)
ax2.legend(
    fontsize = "small",
         loc = "lower right",
)
ax2.semilogx()
# ax2.set_xticks(                                                                 # MatPlotLib ≥ 3.5.0
#     [8, 16, 32, 64, 128, 256, 512],                                             # MatPlotLib ≥ 3.5.0
#     labels = [8, 16, 32, 64, 128, 256, 512],                                    # MatPlotLib ≥ 3.5.0
# )                                                                               # MatPlotLib ≥ 3.5.0
ax2.set_xticks([8, 16, 32, 64, 128, 256, 512])                                  # MatPlotLib < 3.5.0
ax2.set_xticklabels([8, 16, 32, 64, 128, 256, 512])                             # MatPlotLib < 3.5.0
ax2.set_ylim(85, 102)
ax2.set_yticks(range(85, 103))

# Configure figure ...
fg.tight_layout()

# Save figure ...
fg.savefig(
    "compareBufferAngularResolutions.png",
           dpi = 300,
    pad_inches = 0.1,
)
matplotlib.pyplot.close(fg)

# Optimize PNG ...
pyguymer3.image.optimize_image("compareBufferAngularResolutions.png", strip = True)
