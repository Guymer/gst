def save_allLands(fname, dist, debug = False, detailed = False, nang = 19, res = "110m", simp = 0.1):
    """Save buffered (and optionally simplified) land to a compressed WKB file.

    Parameters
    ----------
    fname : string
            the filename of the compressed WKB file
    dist : float
            the distance to buffer the land by (in metres)
    debug : bool, optional
            print debug messages
    detailed : bool, optional
            take account of minor islands
    nang : int, optional
            the number of angles around each point that are calculated when buffering
    res : string, optional
            the resolution of the Natural Earth datasets
    simp : float, optional
            how much intermediary [Multi]Polygons are simplified by; negative values disable simplification (in degrees)
    """

    # Import standard modules ...
    import gzip

    # Import special modules ...
    try:
        import cartopy
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
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

    # Initialize list ...
    sfiles = []

    # Find file containing all the land (and major islands) as [Multi]Polygons ...
    sfiles.append(cartopy.io.shapereader.natural_earth(resolution = res, category = "physical", name = "land"))

    # Check if the user wants to be detailed ...
    if detailed:
        # Find file containing all the minor islands as [Multi]Polygons ...
        sfiles.append(cartopy.io.shapereader.natural_earth(resolution = res, category = "physical", name = "minor_islands"))

    # **************************************************************************

    # Initialize list ...
    buffs = []

    # Loop over Shapefiles ...
    for sfile in sfiles:
        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Skip bad records ...
            if not record.geometry.is_valid:
                print(f"WARNING: Skipping a piece of land in \"{sfile}\" as it is not valid.")
                continue

            # Buffer [Multi]Polygon ...
            buff = pyguymer3.geo.buffer(record.geometry, dist, debug = debug, nang = nang, simp = simp)

            # Check the type of the buffered [Multi]Polygon ...
            if isinstance(buff, shapely.geometry.multipolygon.MultiPolygon):
                # Loop over Polygons ...
                for geom in buff.geoms:
                    # Catch bad Polygons ...
                    if not geom.is_valid:
                        raise Exception("\"geom\" is not a valid Polygon ({0:s})".format(shapely.validation.explain_validity(geom))) from None

                    # Append a Polygon made of only the exterior of this Polygon
                    # to the list ...
                    buffs.append(shapely.geometry.polygon.Polygon(geom.exterior))
            elif isinstance(buff, shapely.geometry.polygon.Polygon):
                # Catch bad Polygons ...
                if not buff.is_valid:
                    raise Exception("\"buff\" is not a valid Polygon ({0:s})".format(shapely.validation.explain_validity(buff))) from None

                # Append a Polygon made of only the exterior of this Polygon to
                # the list ...
                buffs.append(shapely.geometry.polygon.Polygon(buff.exterior))
            else:
                raise TypeError("\"buff\" is an unexpected type") from None

    # Convert list of Polygons to (unified) MultiPolygon ...
    buffs = shapely.ops.unary_union(buffs)

    # Save MultiPolygon ...
    gzip.open(fname, "wb", compresslevel = 9).write(shapely.wkb.dumps(buffs))
