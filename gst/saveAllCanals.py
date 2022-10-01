def saveAllCanals(fname, kwArgCheck = None, debug = False, res = "110m", simp = 0.1, tol = 1.0e-10):
    """Save (optionally simplified) canals to a compressed WKB file.

    Parameters
    ----------
    fname : string
        the file name of the compressed WKB file
    debug : bool, optional
        print debug messages
    res : string, optional
        the resolution of the Natural Earth datasets
    simp : float, optional
        how much intermediary [Multi]LineStrings are simplified by; negative
        values disable simplification (in degrees)
    tol : float, optional
        the Euclidean distance that defines two points as being the same (in
        degrees)
    """

    # Import standard modules ...
    import gzip

    # Import special modules ...
    try:
        import cartopy
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
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

    # Check keyword arguments ...
    if kwArgCheck is not None:
        print(f"WARNING: \"{__name__}\" has been called with an extra positional argument")

    # **************************************************************************

    # Initialize list ...
    lines = []

    # Define Shapefile ...
    sfile = cartopy.io.shapereader.natural_earth(
          category = "physical",
              name = "rivers_lake_centerlines",
        resolution = res,
    )

    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(sfile).records():
        # Skip bad records ...
        if record.geometry is None:
            print(f"WARNING: Skipping a collection of rivers in \"{sfile}\" as it is None.")
            continue
        if not record.geometry.is_valid:
            print(f"WARNING: Skipping a collection of rivers in \"{sfile}\" as it is not valid.")
            continue
        if record.geometry.is_empty:
            print(f"WARNING: Skipping a collection of rivers in \"{sfile}\" as it is empty.")
            continue

        # Check type ...
        if not isinstance(record.geometry, shapely.geometry.linestring.LineString) and not isinstance(record.geometry, shapely.geometry.multilinestring.MultiLineString):
            print(f"WARNING: Skipping a collection of rivers in \"{sfile}\" as it is not a [Multi]LineString.")
            continue

        # Create short-hand ...
        neName = pyguymer3.geo.getRecordAttribute(record, "NAME")

        # Skip if it is not one of the canals of interest ...
        if neName not in ["Panama Canal", "Suez Canal"]:
            continue

        # Loop over LineStrings ...
        for line in pyguymer3.geo.extract_lines(record.geometry):
            # Skip bad LineStrings ...
            if line is None:
                print(f"WARNING: Skipping a river in \"{sfile}\" as it is None.")
                continue
            if not line.is_valid:
                print(f"WARNING: Skipping a river in \"{sfile}\" as it is not valid.")
                continue
            if line.is_empty:
                print(f"WARNING: Skipping a river in \"{sfile}\" as it is empty.")
                continue

            # Append LineString to list ...
            lines.append(line)

    # Return if there aren't any canals at this resolution ...
    if len(lines) == 0:
        return False

    # TODO: Need to extend the end points further out to endsure that the bays
    #       and lagoons around the entrances do not get buffered and block off
    #       the canals.

    # Convert list of LineStrings to a (unified) MultiLineString ...
    lines = shapely.ops.unary_union(lines).simplify(tol)
    if debug:
        pyguymer3.geo.check(lines)

    # Check if the user wants to simplify the MultiLineString ...
    if simp > 0.0:
        # Simplify MultiLineString ...
        linesSimp = lines.simplify(simp)
        if debug:
            pyguymer3.geo.check(linesSimp)

        # Save simplified MultiLineString ...
        with gzip.open(fname, "wb", compresslevel = 9) as fObj:
            fObj.write(shapely.wkb.dumps(linesSimp))

        # Return ...
        return True

    # Save MultiLineString ...
    with gzip.open(fname, "wb", compresslevel = 9) as fObj:
        fObj.write(shapely.wkb.dumps(lines))

    # Return ...
    return True
