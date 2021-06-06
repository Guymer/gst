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

    # Return polygon ...
    return poly
