def remove_interior_rings(poly):
    """Remove all interior rings from a [Multi]Polygon

    This function reads in a [Multi]Polygon and returns a [Multi]Polygon which
    is identical except that it no longer has any interior rings.

    Parameters
    ----------
    poly : shapely.geometry.multipolygon.MultiPolygon
            the input shape

    Returns
    -------
    poly : shapely.geometry.multipolygon.MultiPolygon
            the output shape
    """

    # Import special modules ...
    try:
        import shapely
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Check the input type ...
    if isinstance(poly, shapely.geometry.polygon.Polygon):
        # Return a Polygon made of just the exterior LinearRing ...
        return shapely.geometry.polygon.Polygon(poly.exterior)

    # Check the input type ...
    if isinstance(poly, shapely.geometry.multipolygon.MultiPolygon):
        # Initialize list ...
        polys = []

        # Loop over Polygons ...
        for tmp in poly.geoms:
            # Append a Polygon made of just the exterior LinearRing ...
            polys.append(shapely.geometry.polygon.Polygon(tmp.exterior))

        # Return a MultiPolygon made of Polygons made of just the exterior
        # LinearRings ...
        return shapely.geometry.multipolygon.MultiPolygon(polys)

    # Catch error ...
    raise TypeError("\"poly\" is neither a Polygon nor a MultiPolygon") from None