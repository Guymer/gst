#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.12/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import os

    # Import special modules ...
    try:
        import cartopy
        cartopy.config.update(
            {
                "cache_dir" : os.path.expanduser("~/.local/share/cartopy_cache"),
            }
        )
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                       "backend" : "Agg",                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
                    "figure.dpi" : 300,
                "figure.figsize" : (9.6, 7.2),                                  # NOTE: See https://github.com/Guymer/misc/blob/main/README.md#matplotlib-figure-sizes
                     "font.size" : 8,
            }
        )
        import matplotlib.pyplot
    except:
        raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
    try:
        import shapely
        import shapely.ops
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
        import pyguymer3.image
        import pyguymer3.media
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # Define resolutions ...
    ress = [
        "c",                                # crude
        "l",                                # low
        "i",                                # intermediate
        "h",                                # high
        "f",                                # full
    ]

    # **************************************************************************

    # Initialize list ...
    frames = []

    # Loop over resolutions ...
    for res in ress:
        # Deduce PNG name, append it to the list and skip if it already exists ...
        frame = f"antarctica_res={res}.png"
        frames.append(frame)
        if os.path.exists(frame):
            continue

        print(f"Making \"{frame}\" ...")

        # Create figure ...
        fg = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

        # Initialize list ...
        ax = []

        # Loop over axes ...
        for i in range(6):
            # Check if it is left or right ...
            if i % 2 == 0:
                # Create axis ...
                ax.append(
                    pyguymer3.geo.add_axis(
                        fg,
                        add_coastlines = False,
                                 index = i + 1,
                                 ncols = 2,
                                 nrows = 3,
                    )
                )
            else:
                # Create axis ...
                ax.append(
                    pyguymer3.geo.add_axis(
                        fg,
                        add_coastlines = False,
                                 index = i + 1,
                                   lat = -90.0,
                                   lon =   0.0,
                                 ncols = 2,
                                 nrows = 3,
                    )
                )

            # Configure axis ...
            pyguymer3.geo.add_map_background(
                ax[i],
                      name = "shaded-relief",
                resolution = "large8192px",
            )
            pyguymer3.geo._add_coastlines(                                      # pylint: disable=W0212
                ax[i],
                 edgecolor = "red",
                    levels = [1],
                 linewidth = 1.0,
                resolution = res,
            )

            # Check if it is top, middle or bottom ...
            if i // 2 == 0:
                # Draw Antarctica ...
                pyguymer3.geo._add_coastlines(                                  # pylint: disable=W0212
                    ax[i],
                     edgecolor = "green",
                        levels = [5],
                     linewidth = 1.0,
                    resolution = res,
                )
            elif i // 2 == 1:
                # Draw Antarctica ...
                pyguymer3.geo._add_coastlines(                                  # pylint: disable=W0212
                    ax[i],
                     edgecolor = "blue",
                        levels = [6],
                     linewidth = 1.0,
                    resolution = res,
                )
            else:
                # Initialize list ...
                polys = []

                # Loop over levels ...
                for level in [5, 6]:
                    # Deduce Shapefile name (catching missing datasets) ...
                    sfile = cartopy.io.shapereader.gshhs(
                        level = level,
                        scale = res,
                    )
                    if os.path.basename(sfile) != f"GSHHS_{res}_L{level:d}.shp":
                        print(f" > Skipping \"{sfile}\" (filename does not match request).")
                        continue

                    # Loop over records ...
                    for record in cartopy.io.shapereader.Reader(sfile).records():
                        # Add Polygons to the list ...
                        polys += pyguymer3.geo.extract_polys(record.geometry, onlyValid = True, repair = True)

                # Convert list of Polygons to a (unified) [Multi]Polygon ...
                polys = shapely.ops.unary_union(polys)

                # Plot geometry ...
                # NOTE: Given how "polys" was made, we know that there aren't
                #       any invalid Polygons, so don't bother checking for them.
                ax[i].add_geometries(
                    pyguymer3.geo.extract_polys(polys, onlyValid = False, repair = False),
                    cartopy.crs.PlateCarree(),
                    edgecolor = "cyan",
                    facecolor = "none",
                    linewidth = 1.0,
                )

        # Configure figure ...
        fg.suptitle(f"res={res}")
        fg.tight_layout()

        # Save figure ...
        fg.savefig(frame)
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimise_image(frame, strip = True)

    # **************************************************************************

    print("Making \"antarctica.webp\" ...")

    # Save 1fps WEBP ...
    pyguymer3.media.images2webp(
        frames,
        "antarctica.webp",
        fps = 1.0,
    )

    # Set maximum sizes ...
    # NOTE: By inspection, the PNG frames are 2,160 px tall/wide.
    maxSizes = [512, 1024, 2048]                                                # [px]

    # Loop over maximum sizes ...
    for maxSize in maxSizes:
        print(f"Making \"antarctica{maxSize:04d}px.webp\" ...")

        # Save 1fps WEBP ...
        pyguymer3.media.images2webp(
            frames,
            f"antarctica{maxSize:04d}px.webp",
                     fps = 1.0,
            screenHeight = maxSize,
             screenWidth = maxSize,
        )
