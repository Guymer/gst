def sail(lon, lat, spd, debug = False, detailed = True, dur = 0.2, local = False, nang = 19, nth = 5, ntot = 30, plot = True, res = "110m", simp = 0.1):
    """Sail from a point

    This function reads in a starting coordinate (in degrees) and a sailing
    speed (in knots) and then calculates the maximum possible sailing distance
    on the surface of the Earth that the vessel can reach in the specified time.

    By default, the iteration steps are 12 minutes long and the vessel sails for
    6 hours with contours plotted every hour.

    Parameters
    ----------
    lon : float
            the longitude of the starting point (in degrees)
    lat : float
            the latitude of the starting point (in degrees)
    spd : float
            the speed of the vessel (in knots)
    debug : bool, optional
            print debug messages
    detailed : bool, optional
            take account of minor islands
    dur : float, optional
            the duration between each sailing step (in hours)
    local : bool, optional
            the plot has only local extent
    nang : int, optional
            the number of directions from each point that the vessel could sail in
    nth : int, optional
            plot sailing contours every nth iteration
    ntot : int, optional
            the number of iterations to perform
    plot : bool, optional
            make a plot
    res : string, optional
            resolution of the Natural Earth datasets
    simp : float, optional
            how much intermediary [Multi]Polygon are simplified by (in degrees)
    """

    # Import special modules ...
    try:
        import cartopy
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import matplotlib
        matplotlib.use("Agg")                                                   # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
        import matplotlib.pyplot
    except:
        raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
    try:
        import shapely
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    try:
        import pyguymer3
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # Import sub-functions ...
    from .remove_land import remove_land

    # **************************************************************************

    # Create initial Point ...
    poly = shapely.geometry.point.Point(lon, lat)

    # Create short-hand ...
    dist = 1852.0 * spd * dur                                                   # [m]

    print(f"Iterations will be every {dist:,.1f} metres.")

    # Find file containing all the land (and major islands) polygons ...
    sfiles = [cartopy.io.shapereader.natural_earth(resolution = res, category = "physical", name = "land")]

    # Check if the user wants to be detailed ...
    if detailed:
        # Find file containing all the minor islands polygons ...
        sfiles.append(cartopy.io.shapereader.natural_earth(resolution = res, category = "physical", name = "minor_islands"))

    # **************************************************************************

    # Check if the user wants to make a plot ...
    if plot:
        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = 300)
        if local:
            ax = matplotlib.pyplot.axes(projection = cartopy.crs.Orthographic(central_longitude = lon, central_latitude = lat))
            ext = pyguymer3.buffer(poly, ntot * dist, debug = debug, nang = nang, simp = simp).bounds
            ax.set_extent([ext[0], ext[2], ext[1], ext[3]])
        else:
            ax = matplotlib.pyplot.axes(projection = cartopy.crs.Robinson())
            ax.set_global()
        pyguymer3.add_map_background(ax, resolution = "large4096px")

    # Loop over iterations ...
    for i in range(ntot):
        print(f"Iteration {i + 1:,d}/{ntot:,d} ({(i + 1) * dur:,.1f} hours of sailing) ...")

        # Sail ...
        poly = pyguymer3.buffer(poly, dist, debug = debug, nang = nang, simp = simp)
        poly = remove_land(poly, sfiles)

        # Check if the user wants to make a plot and that this iteration is one
        # of the ones to be plotted ...
        if plot and (i + 1) % nth == 0:
            print("  Plotting ...")

            # Plot [Multi]Polygon ...
            ax.add_geometries([poly], cartopy.crs.PlateCarree(), alpha = 1.0, edgecolor = f"C{((i + 1) // nth) - 1:d}", facecolor = "none", linewidth = 1.0)

    # Check if the user wants to make a plot ...
    if plot:
        print("Saving plot ...")

        # Determine output PNG file name ...
        png = f"dur={dur:f}_nang={nang:d}_nth={nth:d}_ntot={ntot:d}_res={res}_simp={simp:f}.png"

        # Save figure ...
        fg.savefig(png, bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.optimize_image(png, strip = True)
