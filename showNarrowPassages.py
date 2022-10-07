#!/usr/bin/env python3

# Import standard modules ...
import gzip
import os
import subprocess

# Import special modules ...
try:
    import cartopy
except:
    raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
try:
    import matplotlib
    matplotlib.use("Agg")                                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
    import matplotlib.pyplot
except:
    raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
try:
    import shapely
    import shapely.wkb
except:
    raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

# Import my modules ...
try:
    import pyguymer3
    import pyguymer3.geo
    import pyguymer3.image
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# ******************************************************************************

# Define combinations ...
combs = [
    (2.0,  9, 10000.0, (1.0, 0.0, 0.0, 0.5),),
    (4.0, 17,  5000.0, (0.0, 1.0, 0.0, 0.5),),
    (8.0, 33,  2500.0, (0.0, 0.0, 1.0, 0.5),),
]

# Define locations ...
locs = [
    ( 11.8,  55.5),                     # Zealand
    ( -5.6,  36.0),                     # Gibraltar
    (-79.7,   9.1),                     # Panama Canal
    ( 32.3,  30.6),                     # Suez Canal
    ( 43.4,  12.6),                     # Bab-el-Mandeb
    (-69.6, -52.5),                     # Primera Angostura
]                                                                               # [°]

# Define resolutions ...
ress = [
    "c",                                # crude
    "l",                                # low
    "i",                                # intermediate
    "h",                                # high
    "f",                                # full
]

# ******************************************************************************

# Loop over resolutions ...
for res in ress:
    # Loop over combinations ...
    for cons, nang, prec, colour in combs:
        # Populate GST command ...
        cmd = [
            "python3.10", "run.py",
            "-1.0", "+50.5", "20.0",            # depart Portsmouth Harbour at 20 knots
            "--duration", "0.012",              # some sailing
            "--precision", f"{prec:.1f}",       # LOOP VARIABLE
            "--conservatism", f"{cons:.1f}",    # LOOP VARIABLE
            "--freqLand", "1024",               # don't re-evalutate land
            "--freqSimp", "1024",               # don't simplify
            "--nang", f"{nang:d}",              # LOOP VARIABLE
            "--resolution", res,                # LOOP VARIABLE
        ]

        print(f'Running "{" ".join(cmd)}" ...')

        # Run GST ...
        subprocess.run(
            cmd,
               check = False,
            encoding = "utf-8",
              stderr = subprocess.DEVNULL,
              stdout = subprocess.DEVNULL,
        )

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(
            dpi = 300,
        figsize = (12, 8),
    )

    # Initialize lists ...
    ax = []
    ext = []

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
            locs = range(-180, 181, 1),
        )
        pyguymer3.geo.add_vertical_gridlines(
            ax[iloc],
            ext[iloc],
            locs = range(-90, 91, 1),
        )

        # Loop over combinations ...
        for cons, nang, prec, colour in combs:
            # Deduce file name and skip if it is missing ...
            dname = f"res={res}_cons={cons:.2e}_tol=1.00e-10/nang={nang:d}_prec={prec:.2e}"
            fname = f"{dname}/allLands.wkb.gz"
            if not os.path.exists(fname):
                continue

            print(f"Plotting \"{fname}\" ...")

            # Load [Multi]Polygon ...
            with gzip.open(fname, "rb") as fObj:
                allLands = shapely.wkb.loads(fObj.read())

            # Plot Polygons ...
            ax[iloc].add_geometries(
                pyguymer3.geo.extract_polys(allLands),
                cartopy.crs.PlateCarree(),
                edgecolor = (0.0, 0.0, 0.0, 0.5),
                facecolor = colour,
                linewidth = 1.0,
            )

            # Clean up ...
            del allLands

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
        pyguymer3.geo.add_coastlines(
            ax[iloc],
             colorName = "white",
             linewidth = 1.0,
            resolution = "f",
        )
        ax[iloc].set_title(f"lon={loc[0]:+.2f}°, lat={loc[1]:+.2f}°")

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig(
        f"showNarrowPassages_res={res}.png",
               dpi = 300,
        pad_inches = 0.1,
    )
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image(f"showNarrowPassages_res={res}.png", strip = True)
