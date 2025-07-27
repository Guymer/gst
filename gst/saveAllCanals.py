#!/usr/bin/env python3

# Define function ...
def saveAllCanals(
    wName,
    /,
    *,
    debug = __debug__,
     simp = 0.1,
      tol = 1.0e-10,
):
    """Save (optionally simplified) canals to a compressed WKB file.

    Parameters
    ----------
    wName : string
        the file name of the compressed WKB file
    debug : bool, optional
        print debug messages
    simp : float, optional
        how much intermediary [Multi]LineStrings are simplified by; negative
        values disable simplification (in degrees)
    tol : float, optional
        the Euclidean distance that defines two points as being the same (in
        degrees)
    """

    # Import standard modules ...
    import gzip
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
    try:
        import geojson
        geojson.geometry.Geometry.__init__.__defaults__ = (None, False, 12)     # NOTE: See https://github.com/jazzband/geojson/issues/135#issuecomment-596509669
    except:
        raise Exception("\"geojson\" is not installed; run \"pip install --user geojson\"") from None
    try:
        import shapely
        import shapely.geometry
        import shapely.wkb
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # **************************************************************************

    # Create short-hand ...
    gName = f'{wName.removesuffix(".wkb.gz")}.geojson'

    # Initialize dictionary ...
    db = {
        "Panama Canal" : {
            "raw" : [],
            "top" : [],                                                         # [°]
        },
        "Suez Canal" : {
            "raw" : [],
            "top" : [],                                                         # [°]
        },
    }

    # Define Shapefile ...
    sfile = cartopy.io.shapereader.natural_earth(
          category = "physical",
              name = "rivers_lake_centerlines",
        resolution = "10m",
    )

    print(f" > Loading \"{sfile}\" ...")

    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(sfile).records():
        # Create short-hand ...
        neName = pyguymer3.geo.getRecordAttribute(record, "NAME")

        # Skip if it is not one of the canals of interest ...
        if neName not in db:
            continue

        # Loop over LineStrings ...
        for line in pyguymer3.geo.extract_lines(
            record.geometry,
            onlyValid = True,
        ):
            # Append LineString (and its top) to lists ...
            db[neName]["raw"].append(line)
            db[neName]["top"].append(line.bounds[3])                            # [°]

    # **************************************************************************

    # Initialize list ...
    lines = []

    # Loop over canals ...
    for _, info in db.items():
        # Initialize list ...
        coords = []                                                             # [°]

        # Loop over the tops of the raw lines (from North-to-South) ...
        for top in sorted(info["top"])[::-1]:
            # Find the index of this raw line ...
            index = info["top"].index(top)

            # Check if this raw line goes North-to-South or South-to-North ...
            if info["raw"][index].coords[0][1] > info["raw"][index].coords[-1][1]:
                # Loop over coordinates in this raw line (from North-to-South) ...
                for coord in info["raw"][index].coords:
                    # Append coordinate to list ...
                    coords.append(coord)                                        # [°]
            else:
                # Loop over coordinates in this raw line (from North-to-South) ...
                for coord in info["raw"][index].coords[::-1]:
                    # Append coordinate to list ...
                    coords.append(coord)                                        # [°]

        # Make LineString ...
        line = shapely.geometry.linestring.LineString(coords)
        if debug:
            pyguymer3.geo.check(line)

        # Append LineString to list ...
        lines.append(line)

    # **************************************************************************

    # Convert list of LineStrings to a MultiLineString ...
    lines = shapely.geometry.multilinestring.MultiLineString(lines).simplify(tol)
    if debug:
        pyguymer3.geo.check(lines)

    # Check if the user wants to simplify the MultiLineString ...
    if simp > 0.0:
        # Simplify MultiLineString ...
        lines = lines.simplify(simp)
        if debug:
            pyguymer3.geo.check(lines)

    # Save MultiLineString ...
    with gzip.open(wName, mode = "wb", compresslevel = 9) as gzObj:
        gzObj.write(shapely.wkb.dumps(lines))

    # Save MultiLineString ...
    with open(gName, "wt", encoding = "utf-8") as fObj:
        geojson.dump(
            lines,
            fObj,
            ensure_ascii = False,
                  indent = 4,
               sort_keys = True,
        )

    # Return ...
    return True
