#!/usr/bin/env python3

# Import standard modules ...
import glob
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
    import shapely.ops
    import shapely.wkb
except:
    raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

# Import my modules ...
try:
    import gst
except:
    raise Exception("\"gst\" is not installed; you need to have the Python module from https://github.com/Guymer/gst located somewhere in your $PYTHONPATH") from None
try:
    import pyguymer3
    import pyguymer3.geo
    import pyguymer3.image
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# ******************************************************************************

# Define starting location ...
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

# Set Global Self-Consistent, Hierarchical, High-Resolution Geography Shapefile
# list ...
# NOTE: See https://www.ngdc.noaa.gov/mgg/shorelines/gshhs.html
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

# Make output folders ...
if not os.path.exists("compareDatasets/gshhg/records"):
    os.makedirs("compareDatasets/gshhg/records")
if not os.path.exists("compareDatasets/ne/records"):
    os.makedirs("compareDatasets/ne/records")

# ******************************************************************************

# Loop over Global Self-Consistent, Hierarchical, High-Resolution Geography
# Shapefiles ...
for gshhgShapeFile in gshhgShapeFiles:
    print(f" > Loading \"{gshhgShapeFile}\" ...")

    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(gshhgShapeFile).records():
        # Skip bad records ...
        if record.geometry is None:
            print(f"WARNING: Skipping a collection of land in \"{gshhgShapeFile}\" as it is None.")
            continue
        if not record.geometry.is_valid:
            print(f"WARNING: Skipping a collection of land in \"{gshhgShapeFile}\" as it is not valid.")
            continue
        if record.geometry.is_empty:
            print(f"WARNING: Skipping a collection of land in \"{gshhgShapeFile}\" as it is empty.")
            continue

        # Check type ...
        if not isinstance(record.geometry, shapely.geometry.polygon.Polygon) and not isinstance(record.geometry, shapely.geometry.multipolygon.MultiPolygon):
            print(f"WARNING: Skipping a collection of land in \"{gshhgShapeFile}\" as it is not a [Multi]Polygon.")
            continue

        # Deduce temporary file name and skip if it exists already ...
        tname = f"compareDatasets/gshhg/records/{record.geometry.centroid.x:+014.9f},{record.geometry.centroid.y:+013.9f}.wkb.gz"
        if os.path.exists(tname):
            continue

        print(f"   > Making \"{tname}\" ...")

        # Initialize list ...
        polys = []

        # Loop over Polygons ...
        for poly in pyguymer3.geo.extract_polys(record.geometry):
            # Skip bad Polygons ...
            if poly is None:
                print(f"WARNING: Skipping a piece of land in \"{gshhgShapeFile}\" as it is None.")
                continue
            if not poly.is_valid:
                print(f"WARNING: Skipping a piece of land in \"{gshhgShapeFile}\" as it is not valid.")
                continue
            if poly.is_empty:
                print(f"WARNING: Skipping a piece of land in \"{gshhgShapeFile}\" as it is empty.")
                continue

            # Append the Polygon to the list ...
            polys.append(poly)

        # Convert list of Polygons to a (unified) [Multi]Polygon ...
        polys = shapely.ops.unary_union(polys).simplify(tol)
        if debug:
            pyguymer3.geo.check(polys)

        # Save [Multi]Polygon ...
        with gzip.open(tname, "wb", compresslevel = 9) as fObj:
            fObj.write(shapely.wkb.dumps(polys))

# ******************************************************************************

# Loop over Natural Earth Shapefiles ...
for neShapeFile in neShapeFiles:
    print(f" > Loading \"{neShapeFile}\" ...")

    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(neShapeFile).records():
        # Skip bad records ...
        if record.geometry is None:
            print(f"WARNING: Skipping a collection of land in \"{neShapeFile}\" as it is None.")
            continue
        if not record.geometry.is_valid:
            print(f"WARNING: Skipping a collection of land in \"{neShapeFile}\" as it is not valid.")
            continue
        if record.geometry.is_empty:
            print(f"WARNING: Skipping a collection of land in \"{neShapeFile}\" as it is empty.")
            continue

        # Check type ...
        if not isinstance(record.geometry, shapely.geometry.polygon.Polygon) and not isinstance(record.geometry, shapely.geometry.multipolygon.MultiPolygon):
            print(f"WARNING: Skipping a collection of land in \"{neShapeFile}\" as it is not a [Multi]Polygon.")
            continue

        # Deduce temporary file name and skip if it exists already ...
        tname = f"compareDatasets/ne/records/{record.geometry.centroid.x:+014.9f},{record.geometry.centroid.y:+013.9f}.wkb.gz"
        if os.path.exists(tname):
            continue

        print(f"   > Making \"{tname}\" ...")

        # Initialize list ...
        polys = []

        # Loop over Polygons ...
        for poly in pyguymer3.geo.extract_polys(record.geometry):
            # Skip bad Polygons ...
            if poly is None:
                print(f"WARNING: Skipping a piece of land in \"{neShapeFile}\" as it is None.")
                continue
            if not poly.is_valid:
                print(f"WARNING: Skipping a piece of land in \"{neShapeFile}\" as it is not valid.")
                continue
            if poly.is_empty:
                print(f"WARNING: Skipping a piece of land in \"{neShapeFile}\" as it is empty.")
                continue

            # Append the Polygon to the list ...
            polys.append(poly)

        # Convert list of Polygons to a (unified) [Multi]Polygon ...
        polys = shapely.ops.unary_union(polys).simplify(tol)
        if debug:
            pyguymer3.geo.check(polys)

        # Save [Multi]Polygon ...
        with gzip.open(tname, "wb", compresslevel = 9) as fObj:
            fObj.write(shapely.wkb.dumps(polys))

# ******************************************************************************

# Loop over datasets ...
for dataset in ["gshhg", "ne"]:
    # Deduce file name and skip if it exists already ...
    fname = f"compareDatasets/{dataset}/allLands.wkb.gz"
    if os.path.exists(fname):
        continue

    print(f" > Making \"{fname}\" ...")

    # Initialize list ...
    polys = []

    # Loop over temporary compressed WKB files ...
    for tname in sorted(glob.glob(f"compareDatasets/{dataset}/records/????.?????????,???.?????????.wkb.gz")):
        print(f" > Loading \"{tname}\" ...")

        # Add the individual Polygons to the list ...
        with gzip.open(tname, "rb") as fObj:
            polys += pyguymer3.geo.extract_polys(shapely.wkb.loads(fObj.read()))

    # Cry if there isn't any land at this resolution ...
    if len(polys) == 0:
        raise Exception(f"there aren't any Polygons in the \"{dataset}\" dataset") from None

    # Convert list of Polygons to a (unified) [Multi]Polygon ...
    polys = shapely.ops.unary_union(polys).simplify(tol)
    polys = gst.removeInteriorRings(polys)
    if debug:
        pyguymer3.geo.check(polys)

    # Save [Multi]Polygon ...
    with gzip.open(fname, "wb", compresslevel = 9) as fObj:
        fObj.write(shapely.wkb.dumps(polys))

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

# Load [Multi]Polygon ...
with gzip.open("compareDatasets/gshhg/allLands.wkb.gz", "rb") as fObj:
    polys = pyguymer3.geo.extract_polys(shapely.wkb.loads(fObj.read()))

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

# Load [Multi]Polygon ...
with gzip.open("compareDatasets/ne/allLands.wkb.gz", "rb") as fObj:
    polys = pyguymer3.geo.extract_polys(shapely.wkb.loads(fObj.read()))

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

# Plot the starting location ...
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
