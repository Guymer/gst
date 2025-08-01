# Global Sailing Times (GST)

!["mypy" GitHub Action Status](https://github.com/Guymer/gst/actions/workflows/mypy.yaml/badge.svg) !["pylint" GitHub Action Status](https://github.com/Guymer/gst/actions/workflows/pylint.yaml/badge.svg) !["shellcheck" GitHub Action Status](https://github.com/Guymer/gst/actions/workflows/shellcheck.yaml/badge.svg)

This project aims to show how a vessel sails around the globe.

You can run [runs.sh](runs.sh) to run GST multiple times to generate the output to make the plots, however, this will take many days - so I wouldn't bother. Feel free to have a read of it though.

The `_points2polys()` function in [PyGuymer3](https://github.com/Guymer/PyGuymer3), which is called by the `buffer()` function in [PyGuymer3](https://github.com/Guymer/PyGuymer3), changes *how* it turns an array of points into a Polygon when the buffering distance (in one go) is large (currently defined as more than 10,001.5 kilometres). At a speed of 20.0 knots, you will have gone 9,778.56 kilometres in 11 days and 10,667.52 kilometres in 12 days. To one decimal place, this threshold is crossed between 11.2 days and 11.3 days of sailing at 20.0 knots.

## Profiling

If you want to run GST using a profiler and print out the top 10 most time-consuming functions then run:

```sh
# for the first time a command is run ...
python3.12 -m cProfile -o first.log -m gst -1.0 +50.5 20.0 --duration 5.0 > first.out 2> first.err
python3.12 -c 'import pstats; p = pstats.Stats("first.log"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)'

# for the second time a command is run ...
python3.12 -m cProfile -o second.log -m gst -1.0 +50.5 20.0 --duration 5.0 > second.out 2> second.err
python3.12 -c 'import pstats; p = pstats.Stats("second.log"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)'
```

## Running `compareBufferAngularResolutions.py`

To generate the data needed, [compareBufferAngularResolutions.py](compareBufferAngularResolutions.py) will run commands like:

```sh
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nAng 9 --precision 1250.0 --resolution i
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nAng 17 --precision 1250.0 --resolution i
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nAng 33 --precision 1250.0 --resolution i
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nAng 65 --precision 1250.0 --resolution i
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nAng 129 --precision 1250.0 --resolution i
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nAng 257 --precision 1250.0 --resolution i
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80 kilometres.

## Running `compareBufferRadialResolutions.py`

To generate the data needed, [compareBufferRadialResolutions.py](compareBufferRadialResolutions.py) will run commands like:

```sh
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 1536 --freqPlot 16 --freqSimp 1536 --local --nAng 257 --precision 625.0 --resolution i
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 8 --freqSimp 768 --local --nAng 257 --precision 1250.0 --resolution i
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 384 --freqPlot 4 --freqSimp 384 --local --nAng 257 --precision 2500.0 --resolution i
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 192 --freqPlot 2 --freqSimp 192 --local --nAng 257 --precision 5000.0 --resolution i
python3.12 -m gst -1.0 +50.5 20.0 --duration 0.09 --freqLand 96 --freqPlot 1 --freqSimp 96 --local --nAng 257 --precision 10000.0 --resolution i
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80 kilometres.

## Running `complexity.py`

To generate the data needed, [complexity.py](complexity.py) will run commands like:

```sh
python3.12 -m gst 0.0 0.0 20.0 --conservatism 2.0 --duration 0.01 --freqLand 192 --freqSimp 8 --nAng 9 --precision 5000.0 --resolution i
python3.12 -m gst 0.0 0.0 20.0 --conservatism 2.0 --duration 0.01 --freqLand 384 --freqSimp 16 --nAng 17 --precision 2500.0 --resolution i
python3.12 -m gst 0.0 0.0 20.0 --conservatism 2.0 --duration 0.01 --freqLand 768 --freqSimp 32 --nAng 33 --precision 1250.0 --resolution i
```

## Running `showNarrowPassages.py`

To generate the data needed, [showNarrowPassages.py](showNarrowPassages.py) will run commands like:

```sh
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 192 --freqSimp 8 --nAng 9 --precision 5000.0 --resolution c
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 384 --freqSimp 16 --nAng 17 --precision 2500.0 --resolution c
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 768 --freqSimp 32 --nAng 33 --precision 1250.0 --resolution c
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 192 --freqSimp 8 --nAng 9 --precision 5000.0 --resolution l
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 384 --freqSimp 16 --nAng 17 --precision 2500.0 --resolution l
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 768 --freqSimp 32 --nAng 33 --precision 1250.0 --resolution l
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 192 --freqSimp 8 --nAng 9 --precision 5000.0 --resolution i
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 384 --freqSimp 16 --nAng 17 --precision 2500.0 --resolution i
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 768 --freqSimp 32 --nAng 33 --precision 1250.0 --resolution i
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 192 --freqSimp 8 --nAng 9 --precision 5000.0 --resolution h
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 384 --freqSimp 16 --nAng 17 --precision 2500.0 --resolution h
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 768 --freqSimp 32 --nAng 33 --precision 1250.0 --resolution h
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 192 --freqSimp 8 --nAng 9 --precision 5000.0 --resolution f
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 384 --freqSimp 16 --nAng 17 --precision 2500.0 --resolution f
python3.12 -m gst 0.0 0.0 20.0 --duration 0.01 --freqLand 768 --freqSimp 32 --nAng 33 --precision 1250.0 --resolution f
```

## Maximum Sailing Distance

To very quickly find out how far a vessel can sail from Portsmouth Harbour at 20 knots, try running something like:

```sh
python3.12 -m gst       \
    -1.0 +50.5 20.0     \   # depart Portsmouth Harbour at 20 knots
    --duration 11.2     \   # ~maximum distance (20 knots * 11.2 days = 9,956.35 kilometres)
    --freqLand 192      \   # ~daily land re-evaluation (192 * 7.5 minutes = 1 day)
    --freqPlot 8        \   # ~hourly plotting (8 * 7.5 minutes = 1 hour)
    --freqSimp 8        \   # ~hourly simplification (8 * 7.5 minutes = 1 hour)
    --nAng 9            \   # minimum number of angles
    --plot              \   # make a plot
    --precision 5000.0  \   # ~⅛ hour distance steps (20 knots * 7.5 minutes = 4.63 kilometres)
    --resolution c          # crude coastline resolution
```

... to repeat the above study at x2 angular resolution and x2 radial resolution then try running something like:

```sh
python3.12 -m gst       \
    -1.0 +50.5 20.0     \
    --duration 11.2     \
    --freqLand 384      \
    --freqPlot 16       \
    --freqSimp 16       \
    --nAng 17           \   # x2 angular resolution
    --plot              \
    --precision 2500.0  \   # x2 radial resolution
    --resolution c
```

... to repeat the above study at x4 angular resolution and x4 radial resolution then try running something like:

```sh
python3.12 -m gst       \
    -1.0 +50.5 20.0     \
    --duration 11.2     \
    --freqLand 768      \
    --freqPlot 32       \
    --freqSimp 32       \
    --nAng 33           \   # x4 angular resolution
    --plot              \
    --precision 1250.0  \   # x4 radial resolution
    --resolution c
```

Alternatively, if you just want to marvel at the ferries weaving around the islands in Stockholm Archipelago, then try running something like:

```sh
python3.12 -m gst           \
    +18.079 +59.324 20.0    \   # depart Slussen Ferry Terminal at 20 knots
    --duration 0.03         \   # sail for ~¾ hour (20 knots * 0.03 days = 26.67 kilometres)
    --freqLand 3000         \   # re-evaluate land every 30 kilometres (i.e., never)
    --freqPlot 10           \   # plot every 100 metres
    --local                 \   # only plot the local area
    --nAng 33               \   # turn corners smoothly
    --plot                  \   # make a plot
    --precision 10.0        \   # 10 metre distance steps
    --resolution f              # full coastline resolution
```

## Dependencies

GST requires the following Python modules to be installed and available in your `PYTHONPATH`.

* [cartopy](https://pypi.org/project/Cartopy/)
* [geojson](https://pypi.org/project/geojson/)
* [matplotlib](https://pypi.org/project/matplotlib/)
* [numpy](https://pypi.org/project/numpy/)
* [PIL](https://pypi.org/project/Pillow/)
* [pyguymer3](https://github.com/Guymer/PyGuymer3)
* [shapely](https://pypi.org/project/Shapely/)

GST uses some [Global Self-Consistent Hierarchical High-Resolution Geography](https://www.ngdc.noaa.gov/mgg/shorelines/) resources and some [Natural Earth](https://www.naturalearthdata.com/) resources via the [cartopy](https://pypi.org/project/Cartopy/) module. If they do not exist on your system then [cartopy](https://pypi.org/project/Cartopy/) will download them for you in the background. Consequently, a working internet connection may be required the first time you run GST.
