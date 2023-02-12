#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.10/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import special modules ...
    try:
        import cartopy
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                   "backend" : "Agg",                                           # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
                "figure.dpi" : 300,
                 "font.size" : 8,
            }
        )
        import matplotlib.pyplot
    except:
        raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
    try:
        import shapely
        import shapely.geometry
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

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
    fg = matplotlib.pyplot.figure(figsize = (12, 9))

    # Initialize lists ...
    ax = []
    ext = []

    # **************************************************************************

    # Loop over locations ...
    for iloc, loc in enumerate(locs):
        # Create axis ...
        ax.append(
            fg.add_subplot(
                2,
                3,
                iloc + 1,
                projection = cartopy.crs.Orthographic(
                    central_longitude = loc[0],
                     central_latitude = loc[1],
                )
            )
        )

        # Find how large a 100km radius circle is around the central location ...
        point = shapely.geometry.point.Point(loc[0], loc[1])
        poly = pyguymer3.geo.buffer(
            point,
            100.0e3,
            fill = -1.0,
            nang = 9,
            simp = -1.0,
        )

        # Create extent ...
        ext.append(
            [
                poly.bounds[0],         # minx
                poly.bounds[2],         # maxx
                poly.bounds[1],         # miny
                poly.bounds[3],         # maxy
            ]
        )                                                                       # [°]

        # Clean up ...
        del point, poly

        # Configure axis ...
        ax[iloc].set_extent(ext[iloc])
        pyguymer3.geo.add_map_background(
            ax[iloc],
                  name = "shaded-relief",
            resolution = "large8192px",
        )
        pyguymer3.geo.add_horizontal_gridlines(
            ax[iloc],
            ext[iloc],
            locs = range(-90, 91, 1),
        )
        pyguymer3.geo.add_vertical_gridlines(
            ax[iloc],
            ext[iloc],
            locs = range(-180, 181, 1),
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
            fg.add_subplot(
                2,
                3,
                iloc + 3 + 1,
                projection = cartopy.crs.Orthographic(
                    central_longitude = loc[0],
                     central_latitude = loc[1],
                )
            )
        )

        # Find how large a 100km radius circle is around the central location ...
        point = shapely.geometry.point.Point(loc[0], loc[1])
        poly = pyguymer3.geo.buffer(
            point,
            100.0e3,
            fill = -1.0,
            nang = 9,
            simp = -1.0,
        )

        # Create extent ...
        ext.append(
            [
                poly.bounds[0],         # minx
                poly.bounds[2],         # maxx
                poly.bounds[1],         # miny
                poly.bounds[3],         # maxy
            ]
        )                                                                       # [°]

        # Clean up ...
        del point, poly

        # Configure axis ...
        ax[iloc + 3].set_extent(ext[iloc + 3])
        pyguymer3.geo.add_map_background(
            ax[iloc + 3],
                  name = "shaded-relief",
            resolution = "large8192px",
        )
        pyguymer3.geo.add_horizontal_gridlines(
            ax[iloc + 3],
            ext[iloc + 3],
            locs = range(-180, 181, 1),
        )
        pyguymer3.geo.add_vertical_gridlines(
            ax[iloc + 3],
            ext[iloc + 3],
            locs = range(-90, 91, 1),
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
