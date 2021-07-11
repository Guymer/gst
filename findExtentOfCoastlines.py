#!/usr/bin/env python3

# Import special modules ...
try:
    import cartopy
except:
    raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None

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
    cartopy.io.shapereader.natural_earth(resolution = "10m", category = "physical", name = "land"),
    cartopy.io.shapereader.natural_earth(resolution = "10m", category = "physical", name = "minor_islands"),
]

# Loop over Shapefiles ...
for sfile in sfiles:
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
            # Loop over all the individual good Polygons that make up this bad
            # Natural Earth Polygon ...
            for goodPoly in pyguymer3.geo.extract_polys(pyguymer3.geo.remap(badPoly)):
                # Loop over coordinates in the exterior of the good Polygon ...
                for coord in goodPoly.exterior.coords:
                    # Skip un-real points (that only exist to make the
                    # [Multi]Polygon valid in Shapely) ...
                    if abs(coord[0]) > 179.9 or abs(coord[1]) > 89.9:
                        continue

                    # Update variables ...
                    globalMaxY = max(globalMaxY, coord[1])                      # [°]
                    globalMinY = min(globalMinY, coord[1])                      # [°]

print(f"Latitude goes from {globalMinY:.2f}° to {globalMaxY:.2f}°")
