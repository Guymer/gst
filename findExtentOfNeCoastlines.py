#!/usr/bin/env python3

# Import special modules ...
try:
    import cartopy
except:
    raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
try:
    import shapely
except:
    raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

# Import my modules ...
try:
    import pyguymer3
    import pyguymer3.geo
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# Initialize variables ...
globalMaxY = 0.0                                                                # [°]
globalMinY = 0.0                                                                # [°]

# Define Shapefiles ...
sfiles = [
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

# Loop over Shapefiles ...
for sfile in sfiles:
    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(sfile).records():
        # Skip bad records ...
        if record.geometry is None:
            print(f"WARNING: Skipping a collection of land in \"{sfile}\" as it is None.")
            continue
        if not record.geometry.is_valid:
            print(f"WARNING: Skipping a collection of land in \"{sfile}\" as it is not valid.")
            continue
        if record.geometry.is_empty:
            print(f"WARNING: Skipping a collection of land in \"{sfile}\" as it is empty.")
            continue

        # Check type ...
        if not isinstance(record.geometry, shapely.geometry.polygon.Polygon) and not isinstance(record.geometry, shapely.geometry.multipolygon.MultiPolygon):
            print(f"WARNING: Skipping a collection of land in \"{sfile}\" as it is not a [Multi]Polygon.")
            continue

        # Loop over Polygons ...
        for poly in pyguymer3.geo.extract_polys(record.geometry):
            # Skip bad Polygons ...
            if poly is None:
                print(f"WARNING: Skipping a piece of land in \"{sfile}\" as it is None.")
                continue
            if not poly.is_valid:
                print(f"WARNING: Skipping a piece of land in \"{sfile}\" as it is not valid.")
                continue
            if poly.is_empty:
                print(f"WARNING: Skipping a piece of land in \"{sfile}\" as it is empty.")
                continue

            # Loop over coordinates in the exterior of the Polygon ...
            for coord in poly.exterior.coords:
                # Skip un-real points (that only exist to make the
                # [Multi]Polygon valid in Shapely) ...
                if abs(coord[0]) > 179.9 or abs(coord[1]) > 89.9:
                    continue

                # Update variables ...
                globalMaxY = max(globalMaxY, coord[1])                          # [°]
                globalMinY = min(globalMinY, coord[1])                          # [°]

print(f"Latitude goes from {globalMinY:.2f}° to {globalMaxY:.2f}°")
