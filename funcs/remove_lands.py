def remove_lands(poly, lands, simp = 0.1):
    """Remove the parts of a [Multi]Polygon that lie on land

    This function reads in a [Multi]Polygon and a list of Polygons of land
    masses. Each Polygon of land is subtracted from the [Multi]Polygon so as to
    leave only the parts of the [Multi]Polygon that lie on water.

    Parameters
    ----------
    poly : shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon
            the input shape
    lands : list of shapely.geometry.polygon.Polygon
            the list of land masses
    simp : float, optional
            how much intermediary [Multi]Polygons are simplified by; negative values disable simplification (in degrees)

    Returns
    -------
    poly : shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon
            the output shape
    """

    # Import special modules ...
    try:
        import shapely
        import shapely.validation
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Loop over land ...
    for land in lands:
        # Subtract this Polygon from the [Multi]Polygon ...
        poly = poly.difference(land)

    # Check [Multi]Polygon ...
    if not poly.is_valid:
        raise Exception(f"\"poly\" is not a valid [Multi]Polygon ({shapely.validation.explain_validity(poly)})") from None

    # Check [Multi]Polygon ...
    if poly.is_empty:
        raise Exception("\"poly\" is an empty [Multi]Polygon") from None

    # Check if the user wants to simplify the [Multi]Polygon ...
    if simp > 0.0:
        # Simplify [Multi]Polygon ...
        polySimp = poly.simplify(simp)

        # Check simplified [Multi]Polygon ...
        if polySimp.is_valid and not polySimp.is_empty:
            # Return simplified answer ...
            return polySimp

    # Return answer ...
    return poly
