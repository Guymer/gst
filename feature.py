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

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
        import pyguymer3.image
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # **************************************************************************

    # Define locations ...
    locs = [
        (-79.7,  9.1),                  # Panama Canal
        ( 32.3, 30.6),                  # Suez Canal
        ( 29.1, 41.1),                  # Bosporus Strait
    ]                                                                           # [°]

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure()

    # Initialize lists ...
    ax = []
    ext = []

    # **************************************************************************

    # Loop over locations ...
    for iloc, loc in enumerate(locs):
        # Create axis ...
        ax.append(
            pyguymer3.geo.add_axis(
                fg,
                 dist = 100.0e3,
                index = iloc + 1,
                  lat = loc[1],
                  lon = loc[0],
                ncols = 3,
                nrows = 2,
            )
        )

        # Configure axis ...
        pyguymer3.geo.add_map_background(
            ax[iloc],
                  name = "shaded-relief",
            resolution = "large8192px",
        )

        # Find the Shapefile ...
        sfile = cartopy.io.shapereader.gshhs(
            level = 1,
            scale = "f",
        )

        # Initialize list ...
        polys = []

        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Add the Polygons to the list ...
            polys += pyguymer3.geo.extract_polys(record.geometry, onlyValid = True, repair = True)

        # Plot geometry ...
        ax[iloc].add_geometries(
            polys,
            cartopy.crs.PlateCarree(),
            edgecolor = (1.0, 0.0, 0.0, 1.0),
            facecolor = (1.0, 0.0, 0.0, 0.5),
            linewidth = 1.0,
        )

        # Plot the central location ...
        # NOTE: As of 5/Dec/2023, the default "zorder" of the coastlines is 1.5,
        #       the default "zorder" of the gridlines is 2.0 and the default
        #       "zorder" of the scattered points is 1.0.
        ax[iloc].scatter(
            [loc[0]],
            [loc[1]],
                color = "gold",
               marker = "*",
            transform = cartopy.crs.Geodetic(),
               zorder = 5.0,
        )

        # Configure axis ...
        ax[iloc].set_title(f"GSHHG at (lon={loc[0]:+.2f}°, lat={loc[1]:+.2f}°)")

    # **************************************************************************

    # Loop over locations ...
    for iloc, loc in enumerate(locs):
        # Create axis ...
        ax.append(
            pyguymer3.geo.add_axis(
                fg,
                 dist = 100.0e3,
                index = iloc + 3 + 1,
                  lat = loc[1],
                  lon = loc[0],
                ncols = 3,
                nrows = 2,
            )
        )

        # Configure axis ...
        pyguymer3.geo.add_map_background(
            ax[iloc + 3],
                  name = "shaded-relief",
            resolution = "large8192px",
        )

        # Find the Shapefile ...
        sfile = cartopy.io.shapereader.natural_earth(
              category = "physical",
                  name = "land",
            resolution = "10m",
        )

        # Initialize list ...
        polys = []

        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Add the Polygons to the list ...
            polys += pyguymer3.geo.extract_polys(record.geometry, onlyValid = True, repair = True)

        # Plot geometry ...
        ax[iloc + 3].add_geometries(
            polys,
            cartopy.crs.PlateCarree(),
            edgecolor = (1.0, 0.0, 0.0, 1.0),
            facecolor = (1.0, 0.0, 0.0, 0.5),
            linewidth = 1.0,
        )

        # Plot the central location ...
        # NOTE: As of 5/Dec/2023, the default "zorder" of the coastlines is 1.5,
        #       the default "zorder" of the gridlines is 2.0 and the default
        #       "zorder" of the scattered points is 1.0.
        ax[iloc + 3].scatter(
            [loc[0]],
            [loc[1]],
                color = "gold",
               marker = "*",
            transform = cartopy.crs.Geodetic(),
               zorder = 5.0,
        )

        # Configure axis ...
        ax[iloc + 3].set_title(f"NE at (lon={loc[0]:+.2f}°, lat={loc[1]:+.2f}°)")

    # **************************************************************************

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("feature.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image("feature.png", strip = True)
