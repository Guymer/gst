def remove_land(poly, sfiles):
    """Remove the parts of a [Multi]Polygon that lie on land

    This function reads in a [Multi]Polygon and a list of Shapefiles that
    contain records of land. Each record of land is subtracted from the
    [Multi]Polygon so as to leave only the parts of the [Multi]Polygon that lie
    on water.

    Parameters
    ----------
    poly : shapely.geometry.multipolygon.MultiPolygon
            the input shape
    sfiles : list
            the list of Shapefiles

    Returns
    -------
    poly : shapely.geometry.multipolygon.MultiPolygon
            the output shape
    """

    # Import special modules ...
    try:
        import cartopy
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None

    # Loop over Shapefiles ...
    for sfile in sfiles:
        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Subtract the geometry for this record from the [Multi]Polygon ...
            poly = poly.difference(record.geometry)

    # Return polygon ...
    return poly
