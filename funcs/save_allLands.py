def save_allLands(fname, dname, dist, kwArgCheck = None, debug = False, detailed = False, fill = 1.0, nang = 19, res = "110m", simp = 0.1, tol = 1.0e-10):
    """Save buffered (and optionally simplified) land to a compressed WKB file.

    Parameters
    ----------
    fname : string
            the file name of the compressed WKB file
    dname : string
            the directory name where temporary compressed WKB files can be stored
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
    import glob
    import gzip
    import os

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

            # Deduce temporary file name and skip if it exists already ...
            tname = f"{dname}/{record.geometry.centroid.x:+014.9f},{record.geometry.centroid.y:+013.9f}.wkb.gz"
            if os.path.exists(tname):
                continue

            print(f"   > Making \"{tname}\" ...")

            # Initialize list ...
            buffs = []

            # Extract the bad Natural Earth Polygons in this geometry ...
            badPolys = pyguymer3.geo.extract_polys(record.geometry)

            # Loop over all the bad Natural Earth Polygons in this geometry ...
            for ibad, badPoly in enumerate(badPolys):
                print(f"     > Bad Polygon {ibad + 1:,d}/{len(badPolys):,d} has {len(badPoly.exterior.coords):,d} Points ...")

                # Extract the individual good Polygons that make up this bad
                # Natural Earth Polygon ...
                goodPolys = pyguymer3.geo.extract_polys(pyguymer3.geo.remap(badPoly, tol = tol))

                # Loop over all the individual good Polygons that make up this
                # bad Natural Earth Polygon ...
                for igood, goodPoly in enumerate(goodPolys):
                    print(f"       > Good Polygon {igood + 1:,d}/{len(goodPolys):,d} has {len(goodPoly.exterior.coords):,d} Points ...")

                    # Add the individual Polygons that make up the buffer of
                    # this good Polygon to the list ...
                    # NOTE: Don't allow the user to specify the debug mode.
                    buffs += pyguymer3.geo.extract_polys(pyguymer3.geo.buffer(goodPoly, dist, fill = fill, nang = nang, simp = simp, tol = tol))

                # Clean up ...
                del goodPolys

            # Clean up ...
            del badPolys

            # Convert list of Polygons to (unified) [Multi]Polygon ...
            buffs = shapely.ops.unary_union(buffs).simplify(tol)
            if not buffs.is_valid:
                raise Exception(f"\"buffs\" is not a valid [Multi]Polygon ({shapely.validation.explain_validity(buffs)})") from None
            if buffs.is_empty:
                raise Exception("\"buffs\" is an empty [Multi]Polygon") from None

            # Save [Multi]Polygon ...
            gzip.open(tname, "wb", compresslevel = 9).write(shapely.wkb.dumps(buffs))

    # **************************************************************************

    # Initialize list ...
    buffs = []

    # Loop over temporary compressed WKB files ...
    for tname in sorted(glob.glob(f"{dname}/????.?????????,???.?????????.wkb.gz")):
        print(f"   > Loading \"{tname}\" ...")

        # Append the individual Polygons to the list ...
        buffs += pyguymer3.geo.extract_polys(shapely.wkb.loads(gzip.open(tname, "rb").read()))

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
            # Clean up ...
            del buffs

            # Save MultiPolygon ...
            gzip.open(fname, "wb", compresslevel = 9).write(shapely.wkb.dumps(buffsSimp))

            # Clean up ...
            del buffsSimp

            return

        # Clean up ...
        del buffsSimp

        if debug:
            print(f"WARNING: \"buffsSimp\" is not a valid MultiPolygon ({shapely.validation.explain_validity(buffsSimp)}), will return \"buffs\" instead")

    # Save MultiPolygon ...
    gzip.open(fname, "wb", compresslevel = 9).write(shapely.wkb.dumps(buffs))

    # Clean up ...
    del buffs

    return
