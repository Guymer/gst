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
        # Check the type of this geometry ...
        if isinstance(record.geometry, shapely.geometry.polygon.Polygon):
            # Loop over coordinates in the exterior ...
            for coord in record.geometry.exterior.coords:
                # Skip un-real points (that only exist to make the
                # [Multi]Polygon valid in Shapely) ...
                if abs(coord[0]) > 179.9 or abs(coord[1]) > 89.9:
                    continue

                # Update variables ...
                globalMaxY = max(globalMaxY, coord[1])                          # [°]
                globalMinY = min(globalMinY, coord[1])                          # [°]
        elif isinstance(record.geometry, shapely.geometry.multipolygon.MultiPolygon):
            # Loop over geometries ...
            for geom in record.geometry.geoms:
                # Check the type of this geometry ...
                if isinstance(geom, shapely.geometry.polygon.Polygon):
                    # Loop over coordinates in the exterior ...
                    for coord in geom.exterior.coords:
                        # Skip un-real points (that only exist to make the
                        # [Multi]Polygon valid in Shapely) ...
                        if abs(coord[0]) > 179.9 or abs(coord[1]) > 89.9:
                            continue

                        # Update variables ...
                        globalMaxY = max(globalMaxY, coord[1])                  # [°]
                        globalMinY = min(globalMinY, coord[1])                  # [°]
                else:
                    raise Exception(f"\"geom\" is a \"{repr(type(geom))}\"")
        else:
            raise Exception(f"\"record.geometry\" is a \"{repr(type(record.geometry))}\"")

print(f"Land goes from {globalMinY:.2f}° to {globalMaxY:.2f}°")
