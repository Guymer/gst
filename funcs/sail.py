def sail(lon, lat, spd, detailed = True, dur = 0.2, nang = 19, nth = 5, ntot = 30, plot = True, debug = False):
    """Sail from a point

    This function reads in a starting coordinate (in degrees) and a sailing
    speed (in knots) and then calculates the maximum possible sailing distance
    on the surface of the Earth that the vessel can reach in the specified time.

    Parameters
    ----------
    lon : float
            the longitude of the starting point (in degrees)
    lat : float
            the latitude of the starting point (in degrees)
    spd : float
            the speed of the vessel (in knots)
    detailed : bool, optional
            use a detailed description of land
    dur : float, optional
            the duration between each sailing step (in hours)
    nang : int, optional
            the number of angles around each point that the vessel sails in
    nth : int, optional
            plot sailing contours every nth iteration
    ntot : int, optional
            the number of iterations to perform
    plot : bool, optional
            make a plot
    debug : bool, optional
            print debug messages
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

    # Find file containing all the land (and major islands) polygons ...
    sfiles = [cartopy.io.shapereader.natural_earth(resolution = "10m", category = "physical", name = "land")]

    # Check if the user wants to be detailed ...
    if detailed:
        # Find file containing all the minor islands polygons ...
        sfiles.append(cartopy.io.shapereader.natural_earth(resolution = "10m", category = "physical", name = "minor_islands"))

    # **************************************************************************

    # Check if the user wants to make a plot ...
    if plot:
        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = 300)
        ax = matplotlib.pyplot.axes(projection = cartopy.crs.Robinson())
        ax.set_global()
        pyguymer3.add_map_background(ax, resolution = "large4096px")

    # Loop over iterations ...
    for i in range(ntot):
        print(f"Iteration {i + 1:,d}/{ntot:,d} ({(i + 1) * dur:,.1f} hours of sailing) ...")

        # Sail ...
        poly = pyguymer3.buffer(poly, dist, nang = nang, debug = debug)
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

        # Save figure ...
        fg.savefig("gst.png", bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.optimize_image("gst.png", strip = True)
