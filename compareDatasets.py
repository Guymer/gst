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

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
        import pyguymer3.image
    except:
        raise Exception("\"pyguymer3\" is not installed; run \"pip install --user PyGuymer3\"") from None

    # **************************************************************************

    # Define central location ...
    lon = -1.0                                                                  # [°]
    lat = 50.5                                                                  # [°]

    # **************************************************************************

    # Set Global Self-Consistent Hierarchical High-Resolution Geography
    # Shapefile list ...
    # NOTE: See https://www.ngdc.noaa.gov/mgg/shorelines/
    gshhgShapeFiles = [
        cartopy.io.shapereader.gshhs(
            level = 1,
            scale = "f",
        ),
    ]

    # Set Natural Earth Shapefile list ...
    # NOTE: See https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/
    # NOTE: See https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-minor-islands/
    neShapeFiles = [
        cartopy.io.shapereader.natural_earth(
              category = "physical",
                  name = "land",
            resolution = "10m",
        ),
        cartopy.io.shapereader.natural_earth(
              category = "physical",
                  name = "minor_islands",
            resolution = "10m",
        ),
    ]

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

    # Create axis ...
    ax = pyguymer3.geo.add_axis(
        fg,
        add_coastlines = False,
                  dist = 100.0e3,
                   lat = lat,
                   lon = lon,
    )

    # Configure axis ...
    pyguymer3.geo.add_map_background(
        ax,
              name = "shaded-relief",
        resolution = "large8192px",
    )

    # **************************************************************************

    # Loop over Global Self-Consistent Hierarchical High-Resolution Geography
    # Shapefiles ...
    for sfile in gshhgShapeFiles:
        print(f"Loading \"{sfile}\" ...")

        # Initialize list ...
        polys = []

        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Add the Polygons to the list ...
            polys += pyguymer3.geo.extract_polys(record.geometry, onlyValid = True, repair = True)

        # Plot Polygons ...
        ax.add_geometries(
            polys,
            cartopy.crs.PlateCarree(),
            edgecolor = (0.0, 0.0, 0.0, 0.5),
            facecolor = (1.0, 0.0, 0.0, 0.5),
            linewidth = 1.0,
        )

    # **************************************************************************

    # Loop over Natural Earth Shapefiles ...
    for sfile in neShapeFiles:
        print(f"Loading \"{sfile}\" ...")

        # Initialize list ...
        polys = []

        # Loop over records ...
        for record in cartopy.io.shapereader.Reader(sfile).records():
            # Add the Polygons to the list ...
            polys += pyguymer3.geo.extract_polys(record.geometry, onlyValid = True, repair = True)

        # Plot Polygons ...
        ax.add_geometries(
            polys,
            cartopy.crs.PlateCarree(),
            edgecolor = (0.0, 0.0, 0.0, 0.5),
            facecolor = (0.0, 0.0, 1.0, 0.5),
            linewidth = 1.0,
        )

    # **************************************************************************

    # Plot the central location ...
    # NOTE: As of 5/Dec/2023, the default "zorder" of the coastlines is 1.5, the
    #       default "zorder" of the gridlines is 2.0 and the default "zorder" of
    #       the scattered points is 1.0.
    ax.scatter(
        [lon],
        [lat],
            color = "gold",
           marker = "*",
        transform = cartopy.crs.Geodetic(),
           zorder = 5.0,
    )

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("compareDatasets.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimise_image("compareDatasets.png", strip = True)
