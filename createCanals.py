#!/usr/bin/env python3

# Import special modules ...
try:
    import cartopy
except:
    raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
try:
    import geojson
except:
    raise Exception("\"geojson\" is not installed; run \"pip install --user geojson\"") from None
try:
    import shapely
    import shapely.geometry
except:
    raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

# Import my modules ...
try:
    import pyguymer3
    import pyguymer3.geo
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# Initialize list ...
lines = []

# Define Shapefile ...
sfile = cartopy.io.shapereader.natural_earth(
      category = "physical",
          name = "rivers_lake_centerlines",
    resolution = "10m",
)

# Loop over records ...
for record in cartopy.io.shapereader.Reader(sfile).records():
    # Skip bad records ...
    if not record.geometry.is_valid:
        print(f"WARNING: Skipping a collection of rivers in \"{sfile}\" as it is not valid.")
        continue
    if record.geometry.is_empty:
        print(f"WARNING: Skipping a collection of rivers in \"{sfile}\" as it is empty.")
        continue

    # Create short-hand ...
    neName = pyguymer3.geo.getRecordAttribute(record, "NAME")

    # Skip if it is not one of the canals of interest ...
    if neName not in ["Panama Canal", "Suez Canal"]:
        continue

    # Loop over LineStrings ...
    for line in pyguymer3.geo.extract_lines(record.geometry):
        # Skip bad LineStrings ...
        if not line.is_valid:
            print(f"WARNING: Skipping a river in \"{sfile}\" as it is not valid.")
            continue
        if line.is_empty:
            print(f"WARNING: Skipping a river in \"{sfile}\" as it is empty.")
            continue

        # Append LineString to list ...
        lines.append(line)

# Convert list of LineStrings to a MultiLineString ...
lines = shapely.geometry.multilinestring.MultiLineString(lines)

# Save canals of interest ...
with open("createCanals.geojson", "wt", encoding = "utf-8") as fObj:
    geojson.dump(
        lines,
        fObj,
        ensure_ascii = False,
              indent = 4,
           sort_keys = True,
   )
