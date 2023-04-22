#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.11/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
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

    # Import my modules ...
    try:
        import pyguymer3
        import pyguymer3.geo
        import pyguymer3.image
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

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
    fg = matplotlib.pyplot.figure(figsize = (9, 9))

    # Create axis ...
    ax = pyguymer3.geo.add_top_down_axis(
        fg,
        lon,
        lat,
        100.0e3,
    )

    # Configure axis ...
    pyguymer3.geo.add_map_background(
        ax,
              name = "shaded-relief",
        resolution = "large8192px",
    )
    pyguymer3.geo.add_horizontal_gridlines(
        ax,
        locs = [50.0, 50.5, 51.0],
    )
    pyguymer3.geo.add_vertical_gridlines(
        ax,
        locs = [-2.0, -1.5, -1.0, -0.5, 0.0],
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

        # Clean up ...
        del polys

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

        # Clean up ...
        del polys

    # **************************************************************************

    # Plot the central location ...
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
    pyguymer3.image.optimize_image("compareDatasets.png", strip = True)
