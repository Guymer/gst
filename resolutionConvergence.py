#!/usr/bin/env python3

# Import standard modules ...
import glob
import gzip

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
fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = 300)
ax = fg.add_subplot()

# Loop over number of angles (and their colours) ...
for nang, color in [(19, "C0"), (37, "C1"), (91, "C2"), (181, "C3"), (361, "C4")]:
    # Loop over Natural Earth resolutions (and their linestyles) ...
    for res, linestyle in [("110m", "-"), ("50m", "--"), ("10m", "-.")]:
        # Initialize lists ...
        steps = []
        points = []

        # Loop over compressed WKB files ...
        for fname in sorted(glob.glob(f"detailed=F_nang={nang:d}_prec=1.00e+02_res={res}_simp=8.99e-05_tol=1.00e-10/freqFillSimp=25_freqLand=100_lat=+50.700000_lon=-001.000000/contours/istep=??????.wkb.gz")):
            # Load Polygon ...
            ship = shapely.wkb.loads(gzip.open(fname, "rb").read())

            # Append values to lists ...
            steps.append(int(fname.split("/")[-1].split(".")[0].split("=")[1]))
            points.append(len(ship.exterior.coords))

            # Clean up ...
            del ship

        # Check that there are files for this combination ...
        if len(steps) > 0 and len(points) > 0:
            # Plot lists ...
            ax.plot(steps, points, color = color, label = f"nang={nang:d}, res={res}", linestyle = linestyle)

        # Clean up ...
        del steps, points

# Configure axis ...
ax.grid()
ax.legend(fontsize = "small", loc = "lower right")
ax.set_xlabel("Step Number")
ax.set_xlim(0.0)
ax.set_ylabel("Number Of Points In Polygon")
ax.set_ylim(0.0)

# Save figure ...
fg.savefig("resolutionConvergence.png", bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
matplotlib.pyplot.close(fg)

# Optimize PNG ...
pyguymer3.image.optimize_image("resolutionConvergence.png", strip = True)
