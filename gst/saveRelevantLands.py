#!/usr/bin/env python3

# Define function ...
def saveRelevantLands(
    wName,
    ship,
    dist,
    allLands,
    /,
    *,
        debug = __debug__,
         fill = 1.0,
    fillSpace = "EuclideanSpace",
         nAng = 9,
        nIter = 100,
         simp = 0.1,
          tol = 1.0e-10,
):
    """Save relevant land to a compressed WKB file.

    Given a ship and a sailing distance, save a compressed WKB file of all of
    the possible land (surveyed from a list of Polygons) that the ship may
    encounter whilst sailing.

    Parameters
    ----------
    wName : str
        the file name of the compressed WKB file
    ship : shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon
        the ship to sail
    dist : float
        the distance to sail the ship by
    allLands : list of shapely.geometry.polygon.Polygon
        a list of Polygons of land to sail the ship around
    debug : bool, optional
        print debug messages
    fill : float, optional
        how many intermediary points are added to fill in the straight lines
        which connect the points; negative values disable filling
    fillSpace : str, optional
        the geometric space to perform the filling in (either "EuclideanSpace"
        or "GeodesicSpace")
    nAng : int, optional
        the number of angles around each point that are calculated when
        buffering
    simp : float, optional
        how much intermediary [Multi]Polygons are simplified by; negative values
        disable simplification (in degrees)
    tol : float, optional
        the Euclidean distance that defines two points as being the same (in
        degrees)
    """

    # Import standard modules ...
    import gzip

    # Import special modules ...
    try:
        import geojson
    except:
        raise Exception("\"geojson\" is not installed; run \"pip install --user geojson\"") from None
    try:
        import shapely
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

    # **************************************************************************

    # Create short-hand ...
    gName = f'{wName.removesuffix(".wkb.gz")}.geojson'

    # Calculate the maximum possible sailing distance (ignoring all land) ...
    maxShip = pyguymer3.geo.buffer(
        ship,
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

    # **************************************************************************

    # Initialize list ...
    polys = []

    # Loop over Polygons in the MultiPolygon of all of the land ...
    for allLand in allLands:
        # Skip land which is outside of the maximum possible sailing distance of
        # the ship ...
        if maxShip.disjoint(allLand):
            continue

        # Skip land that is wholly contained within the ship (i.e., the ship has
        # already sailed around/past this piece of land) ...
        if ship.contains(allLand):
            continue

        # Append land to list ...
        polys.append(allLand)

    # Convert list of Polygons to a (unified) MultiPolygon ...
    polys = shapely.ops.unary_union(polys).simplify(tol)

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
