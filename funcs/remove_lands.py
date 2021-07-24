def remove_lands(shape, lands, kwArgCheck = None, simp = 0.1):
    """Remove the parts of a shape that lie on land

    This function reads in a shape and a list of Polygons of land masses. Each
    Polygon of land is subtracted from the shape so as to leave only the parts
    of the shape that lie on water.

    Parameters
    ----------
    shape : shapely.geometry.linestring.LineString, shapely.geometry.polygon.LinearRing, shapely.geometry.polygon.Polygon, shapely.geometry.multilinestring.MultiLineString, shapely.geometry.multipolygon.MultiPolygon
            the input shape
    lands : list of shapely.geometry.polygon.Polygon
            the list of land masses
    simp : float, optional
            how much intermediary shapes are simplified by; negative values disable simplification (in degrees)

    Returns
    -------
    shape : shapely.geometry.linestring.LineString, shapely.geometry.polygon.LinearRing, shapely.geometry.polygon.Polygon, shapely.geometry.multilinestring.MultiLineString, shapely.geometry.multipolygon.MultiPolygon
            the output shape
    """

    # Import special modules ...
    try:
        import shapely
        import shapely.validation
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Check keyword arguments ...
    if kwArgCheck is not None:
        print(f"WARNING: \"{__name__}\" has been called with an extra positional argument")

    # **************************************************************************

    # Loop over land ...
    for land in lands:
        # Subtract this Polygon from the shape ...
        shape = shape.difference(land)

    # Check shape ...
    if not shape.is_valid:
        raise Exception(f"\"shape\" is not a valid shape ({shapely.validation.explain_validity(shape)})") from None
    if shape.is_empty:
        raise Exception("\"shape\" is an empty shape") from None

    # Check if the user wants to simplify the shape ...
    if simp > 0.0:
        # Simplify shape ...
        shapeSimp = shape.simplify(simp)

        # Check simplified shape ...
        if shapeSimp.is_valid and not shapeSimp.is_empty:
            # Return simplified answer ...
            return shapeSimp

        # Clean up ...
        del shapeSimp

    # Return answer ...
    return shape
