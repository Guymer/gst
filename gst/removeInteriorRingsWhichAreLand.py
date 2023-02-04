#!/usr/bin/env python3

# Define function ...
def removeInteriorRingsWhichAreLand(shape, lands, /, *, onlyValid = False, prec = 10000.0, repair = False):
    """Remove the holes in a shape which match land

    This function reads in a shape and a list of Polygons of land masses. Each
    Polygon of land is compared with each hole in the shape and a new shape is
    made which does not have any holes which match a land mass.

    Parameters
    ----------
    shape : shapely.geometry.polygon.Polygon, shapely.geometry.multipolygon.MultiPolygon
        the input shape
    lands : list of shapely.geometry.polygon.Polygon
        the list of land masses
    onlyValid : bool, optional
        only return valid Polygons (checks for validity can take a while, if
        being called often)
    prec : float, optional
        the precision of the calculation (in metres)
    repair : bool, optional
        attempt to repair invalid Polygons

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
        # Initialize list ...
        interiors = []

        # Loop over holes in the shape ...
        for interior in shape.interiors:
            # Make a correctly oriented Polygon of the hole in the shape ...
            possibleLand = shapely.geometry.polygon.orient(shapely.geometry.polygon.Polygon(interior))

            # Skip this hole if it is the same as a land mass ...
            skip = False
            for land in lands:
                dist, _, _ = pyguymer3.geo.calc_dist_between_two_locs(
                    land.centroid.x,
                    land.centroid.y,
                    possibleLand.centroid.x,
                    possibleLand.centroid.y,
                )                                                               # [m], [°], [°]
                if dist < prec:
                    skip = True
                    break
            if skip:
                continue

            # Append hole to list ...
            interiors.append(interior)

        # Return a correctly oriented Polygon made up of the exterior LinearRing
        # and the interior LinearRings which are not land ...
        return shapely.geometry.polygon.orient(shapely.geometry.polygon.Polygon(shape.exterior, interiors))

    # Check the input type ...
    if isinstance(shape, shapely.geometry.multipolygon.MultiPolygon):
        # Initialize list ...
        polys = []

        # Loop over Polygons ...
        for poly in pyguymer3.geo.extract_polys(shape, onlyValid = onlyValid, repair = repair):
            # Append a correctly oriented Polygon made up of the exterior
            # LinearRing and the interior LinearRings which are not land ...
            polys.append(removeInteriorRingsWhichAreLand(poly, lands, onlyValid = onlyValid, prec = prec, repair = repair))

        # Return a [Multi]Polygon made of Polygons made of the exterior
        # LinearRing and the interior LinearRings which are not land ...
        return shapely.ops.unary_union(polys)

    # Catch error ...
    raise TypeError(f"\"shape\" is a \"{repr(type(shape))}\"") from None
