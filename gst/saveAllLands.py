def saveAllLands(fname, dname, kwArgCheck = None, allCanals = None, debug = False, dist = -1.0, fill = 1.0, nang = 9, res = "c", simp = 0.1, tol = 1.0e-10):
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
        the resolution of the Global Self-Consistent Hierarchical
        High-Resolution Geography datasets
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
        import geojson
    except:
        raise Exception("\"geojson\" is not installed; run \"pip install --user geojson\"") from None
    try:
        import shapely
        import shapely.wkb
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # Import sub-functions ...
    from .removeInteriorRings import removeInteriorRings

    # Check keyword arguments ...
    if kwArgCheck is not None:
        print(f"WARNING: \"{__name__}\" has been called with an extra positional argument")

    # **************************************************************************

    # Check if the user supplied canals ...
    if isinstance(allCanals, shapely.geometry.multilinestring.MultiLineString):
        # Check if the user wants to buffer the canals ...
        if dist > 0.0:
            # Initialize list ...
            lines = []

            # Loop over canals ...
            for canal in pyguymer3.geo.extract_lines(allCanals):
                # Extract coordinates ...
                coords = list(canal.coords)                                     # [°]

                # Find the bearing from the second coordinate to the first
                # coordinate (assuming that the CoordinateSequence goes from
                # North-to-South) and use it to prepend a starting coordinate
                # even further away ...
                _, bear, _ = pyguymer3.geo.calc_dist_between_two_locs(
                    coords[1][0],
                    coords[1][1],
                    coords[0][0],
                    coords[0][1],
                )                                                               # [°]
                newLon, newLat, _ = pyguymer3.geo.calc_loc_from_loc_and_bearing_and_dist(
                    coords[0][0],
                    coords[0][1],
                    bear,
                    6.0 * dist,         # NOTE: Chosen by trial and error.
                )                                                               # [°], [°]
                coords = [(newLon, newLat)] + coords                            # [°]

                # Find the bearing from the penultimate coordinate to the
                # ultimate coordinate (assuming that the CoordinateSequence goes
                # from North-to-South) and use it to prepend a starting
                # coordinate even further away ...
                _, bear, _ = pyguymer3.geo.calc_dist_between_two_locs(
                    coords[-2][0],
                    coords[-2][1],
                    coords[-1][0],
                    coords[-1][1],
                )                                                               # [°]
                newLon, newLat, _ = pyguymer3.geo.calc_loc_from_loc_and_bearing_and_dist(
                    coords[-1][0],
                    coords[-1][1],
                    bear,
                    6.0 * dist,         # NOTE: Chosen by trial and error.
                )                                                               # [°], [°]
                coords = coords + [(newLon, newLat)]                            # [°]

                # Make LineString ...
                line = shapely.geometry.linestring.LineString(coords)
                if debug:
                    pyguymer3.geo.check(line)

                # Clean up ...
                del coords

                # Append the buffer of the LineString to the list ...
                lines.append(
                    pyguymer3.geo.buffer(
                        line,
                        dist,
                        fill = fill,
                        nang = nang,
                        simp = simp,
                         tol = tol,
                    )
                )

                # Clean up ...
                del line
        else:
            raise Exception("you have provided canals, but no distance to buffer them by") from None
    else:
        # Set list ...
        lines = []

    # **************************************************************************

    # Find file containing all the coastlines as [Multi]Polygons ...
    sfile = cartopy.io.shapereader.gshhs(
        level = 1,
        scale = res,
    )

    # **************************************************************************

    print(f" > Loading \"{sfile}\" ...")

    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(sfile).records():
        # Deduce temporary file name and skip if it exists already ...
        tname = f"{dname}/{record.geometry.centroid.x:+014.9f},{record.geometry.centroid.y:+013.9f}.wkb.gz"
        if os.path.exists(tname):
            continue

        print(f"   > Making \"{tname}\" ...")

        # Initialize list ...
        polys = []

        # Loop over Polygons ...
        for poly in pyguymer3.geo.extract_polys(record.geometry):
            # Check if the user wants to buffer the land ...
            if dist > 0.0:
                # Find the buffer of the land ...
                # NOTE: The land should probably be buffered to prohibit ships
                #       jumping over narrow stretches that are narrower than the
                #       iteration distance.
                poly = pyguymer3.geo.buffer(
                    poly,
                    dist,
                             fill = fill,
                    keepInteriors = False,
                             nang = nang,
                             simp = simp,
                              tol = tol,
                )

            # Loop over canals ...
            for line in lines:
                # Subtract this canal from the [Multi]Polygon ...
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

    # Convert list of Polygons to a (unified) MultiPolygon ...
    polys = shapely.ops.unary_union(polys).simplify(tol)
    polys = removeInteriorRings(polys)
    if debug:
        pyguymer3.geo.check(polys)

    # Check if the user wants to simplify the MultiPolygon ...
    if simp > 0.0:
        # Simplify MultiPolygon ...
        polysSimp = polys.simplify(simp)
        polysSimp = removeInteriorRings(polysSimp)
        if debug:
            pyguymer3.geo.check(polysSimp)

        # Save simplified MultiPolygon ...
        with gzip.open(fname, "wb", compresslevel = 9) as fObj:
            fObj.write(shapely.wkb.dumps(polysSimp))

        # Save MultiPolygon ...
        with open(f"{fname[:-7]}.geojson", "wt", encoding = "utf-8") as fObj:
            geojson.dump(
                polysSimp,
                fObj,
                ensure_ascii = False,
                      indent = 4,
                   sort_keys = True,
            )

        # Return ...
        return True

    # Save MultiPolygon ...
    with gzip.open(fname, "wb", compresslevel = 9) as fObj:
        fObj.write(shapely.wkb.dumps(polys))

    # Save MultiPolygon ...
    with open(f"{fname[:-7]}.geojson", "wt", encoding = "utf-8") as fObj:
        geojson.dump(
            polys,
            fObj,
            ensure_ascii = False,
                  indent = 4,
               sort_keys = True,
        )

    # Return ...
    return True
