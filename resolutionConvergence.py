#!/usr/bin/env python3

# Import standard modules ...
import gzip
import os

# Import special modules ...
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
    import pyguymer3.image
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# Create figure ...
fg = matplotlib.pyplot.figure(
        dpi = 300,
    figsize = (9, 6),
)

# Create axis ...
ax = fg.add_subplot()

# Loop over number of angles ...
for iang, nang in enumerate([9, 13, 17, 37, 89, 181, 361]):
    # Create short-hand ...
    color = f"C{iang:d}"

    # Loop over Natural Earth resolutions (and their linestyles) ...
    for res, linestyle in [("110m", "-"), ("50m", "--"), ("10m", "-.")]:
        # Initialize lists ...
        steps = []
        points = []

        # Loop over distances ...
        for dist in range(8):
            # Deduce file name and skip if it is missing ...
            fname = f"detailed=F_nang={nang:d}_prec=1.00e+04_res={res}_simp=8.99e-04_tol=1.00e-10/freqLand=100_freqSimp=25_lon=-001.000000_lat=+50.700000/contours/istep={dist:06d}.wkb.gz"
            if not os.path.exists(fname):
                continue

            print(f"Surveying \"{fname}\" ...")

            # Load Polygon ...
            with gzip.open(fname, "rb") as fobj:
                ship = shapely.wkb.loads(fobj.read())

            # Append values to lists ...
            steps.append(dist)
            points.append(len(ship.exterior.coords))

            # Clean up ...
            del ship

        # Check that there are files for this combination ...
        if len(steps) > 0 and len(points) > 0:
            # Plot lists ...
            ax.plot(
                steps,
                points,
                    color = color,
                    label = f"nang={nang:d}, res={res}",
                linestyle = linestyle,
            )

        # Clean up ...
        del steps, points

# Configure axis ...
ax.grid()
ax.legend(fontsize = "small", loc = "lower right")
ax.set_xlabel("Step Number")
ax.set_xlim(0, 7)
ax.set_ylabel("Number Of Points In Polygon")
ax.set_ylim(0)

# Configure figure ...
fg.tight_layout()

# Save figure ...
fg.savefig(
    "resolutionConvergence.png",
           dpi = 300,
    pad_inches = 0.1,
)
matplotlib.pyplot.close(fg)

# Optimize PNG ...
pyguymer3.image.optimize_image("resolutionConvergence.png", strip = True)
