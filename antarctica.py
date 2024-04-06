#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.11/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
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
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

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
                    fg.add_subplot(
                        3,
                        2,
                        i + 1,
                        projection = cartopy.crs.Robinson(),
                    )
                )

                # Configure axis ...
                ax[i].set_global()
            else:
                # Create axis ...
                ax.append(
                    pyguymer3.geo.add_top_down_axis(
                        fg,
                          0.0,
                        -90.0,
                        1.0e99,
                        nrows = 3,
                        ncols = 2,
                        index = i + 1,
                    )
                )

            # Configure axis ...
            pyguymer3.geo.add_map_background(
                ax[i],
                      name = "shaded-relief",
                resolution = "large8192px",
            )
            pyguymer3.geo.add_horizontal_gridlines(
                ax[i],
                locs = range(-90, 135, 45),
            )
            pyguymer3.geo.add_vertical_gridlines(
                ax[i],
                locs = range(-180, 225, 45),
            )
            pyguymer3.geo.add_coastlines(
                ax[i],
                 colorName = "red",
                    levels = [1],
                 linewidth = 1.0,
                resolution = res,
            )

            # Check if it is top, middle or bottom ...
            if i // 2 == 0:
                # Draw Antarctica ...
                pyguymer3.geo.add_coastlines(
                    ax[i],
                     colorName = "green",
                        levels = [5],
                     linewidth = 1.0,
                    resolution = res,
                )
            elif i // 2 == 1:
                # Draw Antarctica ...
                pyguymer3.geo.add_coastlines(
                    ax[i],
                     colorName = "blue",
                        levels = [6],
                     linewidth = 1.0,
                    resolution = res,
                )
            else:
                # Initialize list ...
                polys = []

                # Loop over levels ...
                for level in [5, 6]:
                    # Find the Shapefile ...
                    sfile = cartopy.io.shapereader.gshhs(
                        level = level,
                        scale = res,
                    )

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
        pyguymer3.image.optimize_image(frame, strip = True)

    # **************************************************************************

    print("Making \"antarctica.webp\" ...")

    # Save 1fps WEBP ...
    pyguymer3.media.images2webp(
        frames,
        "antarctica.webp",
          fps = 1.0,
        strip = True,
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
                   strip = True,
        )
