def saveAllLands(fname, dname, kwArgCheck = None, allCanals = None, debug = False, detailed = False, dist = -1.0, fill = 1.0, nang = 9, res = "110m", simp = 0.1, tol = 1.0e-10):
    """Save (optionally buffered and optionally simplified) land to a compressed WKB file.

    Parameters
    ----------
    fname : string
        the file name of the compressed WKB file
    dname : string
        the directory name where temporary compressed WKB files can be stored
    allCanals : shapely.geometry.multilinestring.MultiLineString, optional
        a MultiLineString of canals to use to cut up pieces of land to allow
        ships through
    debug : bool, optional
        print debug messages
    detailed : bool, optional
        take account of minor islands
    dist : float, optional
        the distance to buffer the canals by; negative values disable buffering
        (in metres)
    fill : float, optional
        how many intermediary points are added to fill in the straight lines
        which connect the points; negative values disable filling
    nang : int, optional
        the number of angles around each point that are calculated when
        buffering
    res : string, optional
        the resolution of the Natural Earth datasets
    simp : float, optional
        how much intermediary [Multi]Polygons are simplified by; negative values
        disable simplification (in degrees)
    tol : float, optional
        the Euclidean distance that defines two points as being the same (in
        degrees)
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

    # Check if the user supplied canals ...
    if isinstance(allCanals, shapely.geometry.multilinestring.MultiLineString):
        # Check if the user wants to buffer the canals ...
        if dist > 0.0:
            # Add the individual Polygons that make up the buffer of the
            # MultiLineString to the list ...
            lines = pyguymer3.geo.extract_polys(
                pyguymer3.geo.buffer(
                    allCanals,
                    dist,
                    fill = fill,
                    nang = nang,
                    simp = simp,
                     tol = tol,
                )
            )
        else:
            # Add the individual LineStrings that make up the MultiLineString to
            # the list ...
            lines = pyguymer3.geo.extract_lines(allCanals)
    else:
        # Set list ...
        lines = []

    # **************************************************************************

    # Initialize list ...
    sfiles = []

    # Find file containing all the land (and major islands) as [Multi]Polygons ...
    sfiles.append(
        cartopy.io.shapereader.natural_earth(
              category = "physical",
                  name = "land",
            resolution = res,
        )
    )

    # Check if the user wants to be detailed ...
    if detailed:
        # Find file containing all the minor islands as [Multi]Polygons ...
        sfiles.append(
            cartopy.io.shapereader.natural_earth(
                  category = "physical",
                      name = "minor_islands",
                resolution = res,
            )
        )

    # **************************************************************************

    # Loop over Shapefiles ...
    for sfile in sfiles:
        print(f" > Loading \"{sfile}\" ...")

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

            # Deduce temporary file name and skip if it exists already ...
            tname = f"{dname}/{record.geometry.centroid.x:+014.9f},{record.geometry.centroid.y:+013.9f}.wkb.gz"
            if os.path.exists(tname):
                continue

            print(f"   > Making \"{tname}\" ...")

            # Initialize list ...
            polys = []

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

                # TODO: The land should probably be buffered to prohibit ships
                #       jumping over narrow stretches that are narrower than the
                #       iteration distance.

                # Loop over canals ...
                for line in lines:
                    # Subtract this canal from the Polygon ...
                    poly = poly.difference(line)

                # Add the Polygons to the list ...
                polys += pyguymer3.geo.extract_polys(poly)

            # Convert list of Polygons to a (unified) [Multi]Polygon ...
            polys = shapely.ops.unary_union(polys).simplify(tol)
            if debug:
                pyguymer3.geo.check(polys)

            # Save [Multi]Polygon ...
            with gzip.open(tname, "wb", compresslevel = 9) as fObj:
                fObj.write(shapely.wkb.dumps(polys))

    # **************************************************************************

    # Initialize list ...
    polys = []

    # Loop over temporary compressed WKB files ...
    for tname in sorted(glob.glob(f"{dname}/????.?????????,???.?????????.wkb.gz")):
        print(f"   > Loading \"{tname}\" ...")

        # Add the individual Polygons to the list ...
        with gzip.open(tname, "rb") as fObj:
            polys += pyguymer3.geo.extract_polys(shapely.wkb.loads(fObj.read()))

    # Return if there isn't any land at this resolution ...
    if len(polys) == 0:
        return False

    # Convert list of Polygons to a (unified) [Multi]Polygon ...
    polys = shapely.ops.unary_union(polys).simplify(tol)
    if debug:
        pyguymer3.geo.check(polys)

    # Check if the user wants to simplify the [Multi]Polygon ...
    if simp > 0.0:
        # Simplify [Multi]Polygon ...
        polysSimp = polys.simplify(simp)
        if debug:
            pyguymer3.geo.check(polysSimp)

        # Save simplified [Multi]Polygon ...
        with gzip.open(fname, "wb", compresslevel = 9) as fObj:
            fObj.write(shapely.wkb.dumps(polysSimp))

        # Return ...
        return True

    # Save [Multi]Polygon ...
    with gzip.open(fname, "wb", compresslevel = 9) as fObj:
        fObj.write(shapely.wkb.dumps(polys))

    # Return ...
    return True
