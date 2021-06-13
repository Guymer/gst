def remove_lands(poly, lands, simp = 0.1):
    """Remove the parts of a [Multi]Polygon that lie on land

    This function reads in a [Multi]Polygon and a list of Polygons of land
    masses. Each Polygon of land is subtracted from the [Multi]Polygon so as to
    leave only the parts of the [Multi]Polygon that lie on water.

    Parameters
    ----------
    poly : shapely.geometry.multipolygon.MultiPolygon
            the input shape
    lands : list of shapely.geometry.polygon.Polygon
            the list of land masses
    simp : float, optional
            how much intermediary [Multi]Polygons are simplified by; negative values disable simplification (in degrees)

    Returns
    -------
    poly : shapely.geometry.multipolygon.MultiPolygon
            the output shape
    """

    # Loop over land ...
    for land in lands:
        # Subtract this Polygon from the [Multi]Polygon ...
        poly = poly.difference(land)

    # Check if the user wants to simplify the [Multi]Polygon ...
    if simp > 0.0:
        # Simplify [Multi]Polygon ...
        polySimp = poly.simplify(simp)

        # Check simplified [Multi]Polygon ...
        if polySimp.is_valid:
            # Return simplified answer ...
            return polySimp

    # Return answer ...
    return poly
