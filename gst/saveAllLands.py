#!/usr/bin/env python3

# Define function ...
def saveAllLands(
    wName,
    dname,
    /,
    *,
    allCanals = None,
        debug = __debug__,
         dist = -1.0,
         fill = 1.0,
    fillSpace = "EuclideanSpace",
       levels = (1, 5, 6,),
        local = False,
      maxShip = None,
         nAng = 9,
        nIter = 100,
          res = "c",
         simp = 0.1,
          tol = 1.0e-10,
):
    """Save (optionally buffered and optionally simplified) land (with canals
    optionally subtracted) to a compressed WKB file.

    Parameters
    ----------
    wName : str
        the file name of the compressed WKB file
    dname : str
        the directory name where temporary compressed WKB files can be stored
    allCanals : list of shapely.geometry.linestring.LineString, optional
        a MultiLineString of canals to use to cut up pieces of land to allow
        ships through
    debug : bool, optional
        print debug messages
    dist : float, optional
        the distance to buffer the canals and the land by; negative values
        disable buffering (in metres)
    fill : float, optional
        how many intermediary points are added to fill in the straight lines
        which connect the points; negative values disable filling
    fillSpace : str, optional
        the geometric space to perform the filling in (either "EuclideanSpace"
        or "GeodesicSpace")
    levels : tuple of int, optional
        the GSHHG levels to include (you should probably use more than just
        level 1, as it does not contain any representation of Antarctica at all)
    local : bool, optional
        the plot has only local extent
    maxShip : shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon
        the maximum possible sailing distance (ignoring all land)
    nAng : int, optional
        the number of angles around each point that are calculated when
        buffering
    nIter : int, optional
        the maximum number of iterations (particularly the Vincenty formula)
    res : str, optional
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
    import pathlib

    # Import special modules ...
    try:
        import cartopy
        cartopy.config.update(
            {
                "cache_dir" : pathlib.PosixPath("~/.local/share/cartopy").expanduser(),
            }
        )
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import geojson
    except:
        raise Exception("\"geojson\" is not installed; run \"pip install --user geojson\"") from None
    try:
        import shapely
        import shapely.geometry
        import shapely.ops
        import shapely.wkb
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # Import sub-functions ...
    from .removeInteriorRings import removeInteriorRings

    # **************************************************************************

    # Create short-hand ...
    gName = f'{wName.removesuffix(".wkb.gz")}.geojson'

    # Check if the user supplied canals ...
    if isinstance(allCanals, list):
        # Check if the user wants to buffer the canals ...
        if dist > 0.0:
            # Initialize list ...
            lines = []

            # Loop over canals ...
            for allCanal in allCanals:
                # Extract coordinates ...
                coords = list(allCanal.coords)                                  # [°]

                # Find the bearing from the second coordinate to the first
                # coordinate (assuming that the CoordinateSequence goes from
                # North-to-South) and use it to prepend a starting coordinate
                # even further away ...
                _, bear, _ = pyguymer3.geo.calc_dist_between_two_locs(
                    coords[1][0],
                    coords[1][1],
                    coords[0][0],
                    coords[0][1],
                    nIter = nIter,
                )                                                               # [°]
                newLon, newLat, _ = pyguymer3.geo.calc_loc_from_loc_and_bearing_and_dist(
                    coords[0][0],
                    coords[0][1],
                    bear,
                    30000.0,            # NOTE: Chosen by trial and error.
                    nIter = nIter,
                )                                                               # [°], [°]
                coords = [(newLon, newLat)] + coords                            # [°]

                # Find the bearing from the penultimate coordinate to the
                # ultimate coordinate (assuming that the CoordinateSequence goes
                # from North-to-South) and use it to append a finishing
                # coordinate even further away ...
                _, bear, _ = pyguymer3.geo.calc_dist_between_two_locs(
                    coords[-2][0],
                    coords[-2][1],
                    coords[-1][0],
                    coords[-1][1],
                    nIter = nIter,
                )                                                               # [°]
                newLon, newLat, _ = pyguymer3.geo.calc_loc_from_loc_and_bearing_and_dist(
                    coords[-1][0],
                    coords[-1][1],
                    bear,
                    30000.0,            # NOTE: Chosen by trial and error.
                    nIter = nIter,
                )                                                               # [°], [°]
                coords = coords + [(newLon, newLat)]                            # [°]

                # Append a finishing coordinate due South even further away ...
                newLon, newLat, _ = pyguymer3.geo.calc_loc_from_loc_and_bearing_and_dist(
                    coords[-1][0],
                    coords[-1][1],
                    180.0,
                    30000.0,            # NOTE: Chosen by trial and error.
                    nIter = nIter,
                )                                                               # [°], [°]
                coords = coords + [(newLon, newLat)]                            # [°]

                # Make LineString ...
                line = shapely.geometry.linestring.LineString(coords)
                if debug:
                    pyguymer3.geo.check(line)

                # Append the buffer of the LineString to the list ...
                lines.append(
                    pyguymer3.geo.buffer(
                        line,
                        dist,
                                debug = debug,
                                 fill = fill,
                            fillSpace = fillSpace,
                        keepInteriors = True,
                                 nAng = nAng,
                                nIter = nIter,
                                 simp = simp,
                                  tol = tol,
                    )
                )
        else:
            raise Exception("you have provided canals, but no distance to buffer them by") from None
    else:
        # Set list ...
        lines = []

    # **************************************************************************

    # Loop over levels ...
    for level in levels:
        # Deduce Shapefile name (catching missing datasets) ...
        sfile = cartopy.io.shapereader.gshhs(
            level = level,
            scale = res,
        )
        if os.path.basename(sfile) != f"GSHHS_{res}_L{level:d}.shp":
            print(f" > Skipping \"{sfile}\" (filename does not match request).")
            continue

        # **********************************************************************

        print(f" > Loading \"{sfile}\" ...")

        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Deduce temporary file name and skip record if it exists already ...
            tmpName = f"{dname}/{record.geometry.centroid.x:+011.6f},{record.geometry.centroid.y:+010.6f},{record.geometry.area:012.7f}.wkb.gz"
            if os.path.exists(tmpName):
                continue

            print(f"   > Making \"{tmpName}\" ...")

            # Initialize list ...
            polys = []

            # Loop over Polygons ...
            for poly in pyguymer3.geo.extract_polys(
                record.geometry,
                onlyValid = True,
                   repair = True,
            ):
                # Check if only Polygons local to the ship should be saved ...
                if local and maxShip is not None:
                    # Skip Polygon if it is outside of the maximum possible
                    # sailing distance of the ship ...
                    if maxShip.disjoint(poly):
                        continue

                    # Throw away all parts of the Polygon that the ship will
                    # never sail to ...
                    poly = maxShip.intersection(poly)

                # Check if the user wants to buffer the land ...
                # NOTE: The land should probably be buffered to prohibit ships
                #       jumping over narrow stretches that are narrower than the
                #       iteration distance.
                if dist > 0.0:
                    # Find the buffer of the land ...
                    poly = pyguymer3.geo.buffer(
                        poly,
                        dist,
                                debug = debug,
                                 fill = fill,
                            fillSpace = fillSpace,
                        keepInteriors = False,
                                 nAng = nAng,
                                nIter = nIter,
                                 simp = simp,
                                  tol = tol,
                    )

                # Loop over canals ...
                for line in lines:
                    # Subtract this canal from the [Multi]Polygon ...
                    poly = poly.difference(line)

                # Add the Polygons to the list ...
                # NOTE: Given how "poly" was made, we know that there aren't any
                #       invalid Polygons, so don't bother checking for them.
                polys += pyguymer3.geo.extract_polys(
                    poly,
                    onlyValid = False,
                       repair = False,
                )

            # Skip record if it does not have any Polygons ...
            if not polys:
                print("     > Skipped (no Polygons).")
                continue

            # Convert list of Polygons to a (unified) [Multi]Polygon ...
            polys = shapely.ops.unary_union(polys).simplify(tol)
            if debug:
                pyguymer3.geo.check(polys)

            # Save [Multi]Polygon ...
            with gzip.open(tmpName, mode = "wb", compresslevel = 9) as gzObj:
                gzObj.write(shapely.wkb.dumps(polys))

    # **************************************************************************

    # Initialize list ...
    polys = []

    # Loop over temporary compressed WKB files ...
    for tmpName in sorted(glob.glob(f"{dname}/????.??????,???.??????,????.???????.wkb.gz")):
        print(f" > Loading \"{tmpName}\" ...")

        # Add the individual Polygons to the list ...
        # NOTE: Given how "polys" was made, we know that there aren't any
        #       invalid Polygons, so don't bother checking for them.
        with gzip.open(tmpName, mode = "rb") as gzObj:
            polys += pyguymer3.geo.extract_polys(
                shapely.wkb.loads(gzObj.read()),
                onlyValid = False,
                   repair = False,
            )

    # Return if there isn't any land at this resolution ...
    if not polys:
        return False

    # Convert list of Polygons to a (unified) MultiPolygon ...
    # NOTE: Given how "polys" was made, we know that there aren't any invalid
    #       Polygons, so don't bother checking for them.
    polys = shapely.ops.unary_union(polys).simplify(tol)
    polys = removeInteriorRings(
        polys,
        onlyValid = False,
           repair = False,
    )
    if debug:
        pyguymer3.geo.check(polys)

    # Check if the user wants to simplify the MultiPolygon ...
    if simp > 0.0:
        # Simplify MultiPolygon ...
        # NOTE: Given how "polys" was made, we know that there aren't any
        #       invalid Polygons, so don't bother checking for them.
        polys = polys.simplify(simp)
        polys = removeInteriorRings(
            polys,
            onlyValid = False,
               repair = False,
        )
        if debug:
            pyguymer3.geo.check(polys)

    # Save MultiPolygon ...
    with gzip.open(wName, mode = "wb", compresslevel = 9) as gzObj:
        gzObj.write(shapely.wkb.dumps(polys))

    # Save MultiPolygon ...
    with open(gName, "wt", encoding = "utf-8") as fObj:
        geojson.dump(
            polys,
            fObj,
            ensure_ascii = False,
                  indent = 4,
               sort_keys = True,
        )

    # Return ...
    return True
