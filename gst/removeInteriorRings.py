def removeInteriorRings(shape):
    """Remove all interior rings from a [Multi]Polygon

    This function reads in a [Multi]Polygon and returns a [Multi]Polygon which
    is identical except that it no longer has any interior rings.

    Parameters
    ----------
    shape : shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon
        the input shape

    Returns
    -------
    shape : shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon
        the output shape
    """

    # Import special modules ...
    try:
        import shapely
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # **************************************************************************

    # Check the input type ...
    if isinstance(shape, shapely.geometry.polygon.Polygon):
        # Return a correctly oriented Polygon made up of just the exterior
        # LinearRing ...
        return shapely.geometry.polygon.orient(shapely.geometry.polygon.Polygon(shape.exterior))

    # Check the input type ...
    if isinstance(shape, shapely.geometry.multipolygon.MultiPolygon):
        # Initialize list ...
        polys = []

        # Loop over Polygons ...
        for poly in pyguymer3.geo.extract_polys(shape, keepInvalid = True):
            # Append a correctly oriented Polygon made up of just the exterior
            # LinearRing ...
            polys.append(shapely.geometry.polygon.orient(shapely.geometry.polygon.Polygon(poly.exterior)))

        # Return a [Multi]Polygon made of Polygons made of just the exterior
        # LinearRings ...
        return shapely.ops.unary_union(polys)

    # Catch error ...
    raise TypeError(f"\"shape\" is a \"{repr(type(shape))}\"") from None
