def load_lands(lands, sfile, simp = 0.1):
    """Load land from a Shapefile

    This function reads in a Shapefile and loops over all [Multi]Polygons,
    appending simplified versions of them to the user-supplied list.

    Parameters
    ----------
    lands : list of shapely.geometry.polygon.Polygon
            the input list of Polygons
    sfile : string
            the Shapefile to load land from
    simp : float, optional
            how much intermediary [Multi]Polygons are simplified by (in degrees)

    Returns
    -------
    lands : list of shapely.geometry.polygon.Polygon
            the output list of Polygons
    """

    # Import special modules ...
    try:
        import cartopy
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import shapely
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Loop over records ...
    for record in cartopy.io.shapereader.Reader(sfile).records():
        # Check the type of this geometry ...
        if isinstance(record.geometry, shapely.geometry.polygon.Polygon):
            # Append simplified Polygon to list ...
            lands.append(record.geometry.simplify(simp))
        elif isinstance(record.geometry, shapely.geometry.multipolygon.MultiPolygon):
            # Loop over geometries ...
            for geom in record.geometry.geoms:
                # Check the type of this geometry ...
                if isinstance(geom, shapely.geometry.polygon.Polygon):
                    # Append simplified Polygon to list ...
                    lands.append(geom.simplify(simp))
                else:
                    raise Exception(f"\"geom\" is a \"{repr(type(geom))}\"")
        else:
            raise Exception(f"\"record.geometry\" is a \"{repr(type(record.geometry))}\"")

    # Return lands ...
    return lands
