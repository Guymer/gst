#!/usr/bin/env python3

# https://github.com/Guymer/PyGuymer3/commit/503264acd541a577dd43fc7f5a6740b16f0f6fa2
# https://github.com/Guymer/fortranlib/commit/63b7d6ca290790e0340a050b4c31ac3106f8747e

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")                                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
    import matplotlib.pyplot
    import numpy
    import shapely
    import shapely.geometry

    import pyguymer3
    import pyguymer3.geo
    import pyguymer3.image

    lon = -1.0
    lat = -50.7

    debug = True
    nang = 21
    tol = 1.0e-9

    # fill = 1.0
    fill = -1.0

    # simp = 9.0e-4
    simp = -1.0

    ship = shapely.geometry.point.Point(lon, lat)

    fg, ax = matplotlib.pyplot.subplots(2, 2, figsize = (12, 8), dpi = 300)
    ax = ax.flatten()

    for i, maxDist in enumerate(range(4382, 4386)):
        print(i, maxDist)

        maxShip = pyguymer3.geo.buffer(ship, float(maxDist) * 1000.0, debug = debug, fill = fill, nang = nang, simp = simp, tol = tol)
        if isinstance(maxShip, shapely.geometry.polygon.Polygon):
            coords = numpy.array(maxShip.exterior.coords)
            ax[i].plot(coords[:, 0], coords[:, 1], color = "C0", marker = ".")
        elif isinstance(maxShip, shapely.geometry.multipolygon.MultiPolygon):
            j = 0
            for poly in maxShip:
                coords = numpy.array(poly.exterior.coords)
                ax[i].plot(coords[:, 0], coords[:, 1], color = f"C{j:d}", marker = ".")
                j += 1
        else:
            raise Exception("unexpected type") from None

        # maxShip2 = pyguymer3.geo.buffer(
        #     pyguymer3.geo.buffer(
        #         pyguymer3.geo.buffer(
        #             pyguymer3.geo.buffer(ship, 0.25 * float(maxDist) * 1000.0, debug = debug, fill = fill, nang = nang, simp = simp, tol = tol),
        #             0.25 * float(maxDist) * 1000.0, debug = debug, fill = fill, nang = nang, simp = simp, tol = tol
        #         ),
        #         0.25 * float(maxDist) * 1000.0, debug = debug, fill = fill, nang = nang, simp = simp, tol = tol
        #     ),
        #     0.25 * float(maxDist) * 1000.0, debug = debug, fill = fill, nang = nang, simp = simp, tol = tol
        # )
        # if isinstance(maxShip2, shapely.geometry.polygon.Polygon):
        #     coords = numpy.array(maxShip2.exterior.coords)
        #     ax[i].plot(coords[:, 0], coords[:, 1], color = "C0", linestyle = "--", marker = ".")
        # elif isinstance(maxShip2, shapely.geometry.multipolygon.MultiPolygon):
        #     j = 0
        #     for poly in maxShip2:
        #         coords = numpy.array(poly.exterior.coords)
        #         ax[i].plot(coords[:, 0], coords[:, 1], color = f"C{j:d}", linestyle = "--", marker = ".")
        #         j += 1
        # else:
        #     raise Exception("unexpected type") from None

        ax[i].scatter([lon], [lat], color = "gold", marker = "*")

        ax[i].grid()
        ax[i].set_xlim(-180.5, +180.5)
        ax[i].set_ylim( -90.5,  +90.5)

    fg.savefig("bug1.png", bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
    matplotlib.pyplot.close(fg)

    pyguymer3.image.optimize_image("bug1.png", strip = True)
