#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import os
    import pathlib

    # Import special modules ...
    try:
        import cartopy
        cartopy.config.update(
            {
                "cache_dir" : pathlib.PosixPath("~/.local/share/cartopy_cache").expanduser(),
            }
        )
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # Initialize variables ...
    globalMaxY = 0.0                                                            # [°]
    globalMinY = 0.0                                                            # [°]

    # Define Shapefiles ...
    sfiles = [
        cartopy.io.shapereader.gshhs(
            level = 1,
            scale = "f",
        ),
    ]

    # Loop over Shapefiles ...
    for sfile in sfiles:
        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Loop over Polygons ...
            for poly in pyguymer3.geo.extract_polys(record.geometry, onlyValid = True, repair = True):
                # Loop over coordinates in the exterior of the Polygon ...
                for coord in poly.exterior.coords:
                    # Skip un-real points (that only exist to make the
                    # [Multi]Polygon valid in Shapely) ...
                    if abs(coord[0]) > 179.9 or abs(coord[1]) > 89.9:
                        continue

                    # Update variables ...
                    globalMaxY = max(globalMaxY, coord[1])                      # [°]
                    globalMinY = min(globalMinY, coord[1])                      # [°]

    print(f"Latitude goes from {globalMinY:.2f}° to {globalMaxY:.2f}°")
