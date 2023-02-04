#!/usr/bin/env python3

# Define function ...
def saveRelevantLands(fname, ship, dist, allLands, /, *, fill = 1.0, nang = 9, simp = 0.1, tol = 1.0e-10):
    """Save relevant land to a compressed WKB file.

    Parameters
    ----------
    fname : string
        the file name of the compressed WKB file
    ship : shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon
        the ship to sail
    dist : float
        the distance to sail the ship by
    allLands : list of shapely.geometry.polygon.Polygon
        a list of Polygons of land to sail the ship around
    fill : float, optional
        how many intermediary points are added to fill in the straight lines
        which connect the points; negative values disable filling
    nang : int, optional
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
        geojson.geometry.Geometry.__init__.__defaults__ = (None, False, 12)     # NOTE: See https://github.com/jazzband/geojson/issues/135#issuecomment-596509669
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

    # **************************************************************************

    # Calculate the maximum possible sailing distance (ignoring all land) ...
    maxShip = pyguymer3.geo.buffer(
        ship,
        dist,
        fill = fill,
        nang = nang,
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

    # Clean up ...
    del maxShip

    # Convert list of Polygons to a (unified) MultiPolygon ...
    polys = shapely.ops.unary_union(polys).simplify(tol)

    # Save MultiPolygon ...
    with gzip.open(fname, "wb", compresslevel = 9) as gzObj:
        gzObj.write(shapely.wkb.dumps(polys))

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
