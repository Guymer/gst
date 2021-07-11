def save_allLands(fname, dist, kwArgCheck = None, debug = False, detailed = False, fill = 1.0, nang = 19, res = "110m", simp = 0.1, tol = 1.0e-10):
    """Save buffered (and optionally simplified) land to a compressed WKB file.

    Parameters
    ----------
    fname : string
            the filename of the compressed WKB file
    dist : float
            the distance to buffer the land by (in metres)
    debug : bool, optional
            print debug messages
    detailed : bool, optional
            take account of minor islands
    fill : float, optional
            how many intermediary points are added to fill in the straight lines which connect the points; negative values disable filling
    nang : int, optional
            the number of angles around each point that are calculated when buffering
    res : string, optional
            the resolution of the Natural Earth datasets
    simp : float, optional
            how much intermediary [Multi]Polygons are simplified by; negative values disable simplification (in degrees)
    tol : float, optional
            the Euclidean distance that defines two points as being the same (in degrees)
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
        import shapely.validation
        import shapely.wkb
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
    sfiles = []

    # Find file containing all the land (and major islands) as [Multi]Polygons ...
    sfiles.append(cartopy.io.shapereader.natural_earth(resolution = res, category = "physical", name = "land"))

    # Check if the user wants to be detailed ...
    if detailed:
        # Find file containing all the minor islands as [Multi]Polygons ...
        sfiles.append(cartopy.io.shapereader.natural_earth(resolution = res, category = "physical", name = "minor_islands"))

    # **************************************************************************

    # Initialize list ...
    buffs = []

    # Loop over Shapefiles ...
    for sfile in sfiles:
        print(f" > Loading \"{sfile}\" ...")

        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Skip bad records ...
            if not record.geometry.is_valid:
                print(f"WARNING: Skipping a piece of land in \"{sfile}\" as it is not valid.")
                continue
            if record.geometry.is_empty:
                print(f"WARNING: Skipping a piece of land in \"{sfile}\" as it is empty.")
                continue

            print(f"   > Buffering shape at ({record.geometry.centroid.x:+011.6f}°,{record.geometry.centroid.y:+010.6f}°) ...")

            # Loop over all the bad Natural Earth Polygons in this geometry ...
            for badPoly in pyguymer3.geo.extract_polys(record.geometry):
                # Loop over all the individual good Polygons that make up this
                # bad Natural Earth Polygon ...
                for goodPoly in pyguymer3.geo.extract_polys(pyguymer3.geo.remap(badPoly)):
                    # Loop over all the individual Polygons that make up the
                    # buffer of this good Polygon ...
                    for buff in pyguymer3.geo.extract_polys(pyguymer3.geo.buffer(goodPoly, dist, debug = debug, fill = fill, nang = nang, simp = simp, tol = tol)):
                        # Append individual Polygon to list ...
                        buffs.append(buff)

    # Convert list of Polygons to (unified) MultiPolygon ...
    buffs = shapely.ops.unary_union(buffs).simplify(tol)
    if not buffs.is_valid:
        raise Exception(f"\"buffs\" is not a valid MultiPolygon ({shapely.validation.explain_validity(buffs)})") from None
    if buffs.is_empty:
        raise Exception("\"buffs\" is an empty MultiPolygon") from None

    # Check if the user wants to simplify the MultiPolygon ...
    if simp > 0.0:
        # Simplify MultiPolygon ...
        buffsSimp = buffs.simplify(simp)

        # Check simplified MultiPolygon ...
        if buffsSimp.is_valid and not buffsSimp.is_empty:
            # Save MultiPolygon ...
            gzip.open(fname, "wb", compresslevel = 9).write(shapely.wkb.dumps(buffsSimp))

        if debug:
            print(f"WARNING: \"buffsSimp\" is not a valid MultiPolygon ({shapely.validation.explain_validity(buffsSimp)}), will return \"buffs\" instead")

    # Save MultiPolygon ...
    gzip.open(fname, "wb", compresslevel = 9).write(shapely.wkb.dumps(buffs))
