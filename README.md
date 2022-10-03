# Global Sailing Times (GST)

This project aims to show how a vessel sails around the globe.

The `buffer()` function in [PyGuymer3](https://github.com/Guymer/PyGuymer3) has a maximum buffer distance (in one go) of 10,001.5 kilometres. At a speed of 20.0 knots, you will have gone 9,778.56 kilometres in 11 days and 10,667.52 kilometres in 12 days.

## Profiling

If you want to run [the example script](run.py) using a profiler and print out the top 10 most time-consuming functions then run:

```
# for the first time a command is run ...
python3.10 -m cProfile -o first.log run.py -1.0 +50.5 20.0 --duration 5.0 > first.out 2> first.err
python3.10 -c 'import pstats; p = pstats.Stats("first.log"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)'

# for the second time a command is run ...
python3.10 -m cProfile -o second.log run.py -1.0 +50.5 20.0 --duration 5.0 > second.out 2> second.err
python3.10 -c 'import pstats; p = pstats.Stats("second.log"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)'
```

## Running `compareBufferAngularResolutions.py`

To generate the data needed, [compareBufferAngularResolutions.py](compareBufferAngularResolutions.py) will run commands like:

```
python3.10 run.py -1.0 +50.5 20.0 --duration 0.09 --precision 1250.0 --nang  9 --resolution 10m
python3.10 run.py -1.0 +50.5 20.0 --duration 0.09 --precision 1250.0 --nang 17 --resolution 10m
python3.10 run.py -1.0 +50.5 20.0 --duration 0.09 --precision 1250.0 --nang 33 --resolution 10m
...
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80 kilometres.

## Running `compareBufferRadialResolutions.py`

To generate the data needed, [compareBufferRadialResolutions.py](compareBufferRadialResolutions.py) will run commands like:

```
python3.10 run.py -1.0 +50.5 20.0 --duration 0.09 --precision 1250.0 --nang 513 --resolution 10m
python3.10 run.py -1.0 +50.5 20.0 --duration 0.09 --precision 2500.0 --nang 513 --resolution 10m
python3.10 run.py -1.0 +50.5 20.0 --duration 0.09 --precision 5000.0 --nang 513 --resolution 10m
...
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80 kilometres.

## Maximum Sailing Distance

To very quickly find out how far a vessel can sail, try running something like:

```
python3.10 run.py       \
    -1.0 +50.5 20.0     \   # depart Portsmouth Harbour at 20 knots
    --duration 11.2     \   # ~maximum distance (20 knots * 11.2 days = 9,956.35 kilometres)
    --precision 10000.0 \   # ~¼ hour distance steps (20 knots * 15 minutes = 9.26 kilometres)
    --conservatism 2.0  \   # some conservatism
    --freqLand 96       \   # ~daily land re-evaluation (96 * 15 minutes = 1 day)
    --freqPlot 4        \   # ~hourly plotting (4 * 15 minutes = 1 hour)
    --freqSimp 4        \   # ~hourly simplification (4 * 15 minutes = 1 hour)
    --nang 9            \   # minimum number of angles
    --plot              \   # make a plot
    --resolution 50m        # coarsest land resolution (that has the Panama Canal and Suez Canal)
```

... to repeat the above studies at x2 angular resolution, x2 radial resolution and x2 conservatism then try running something like:

```
python3.10 run.py       \
    -1.0 +50.5 20.0     \
    --duration 11.2     \
    --precision 5000.0  \   # x2 radial resolution
    --conservatism 4.0  \   # x2 conservatism
    --freqLand 192      \
    --freqPlot 8        \
    --freqSimp 8        \
    --nang 17           \   # x2 angular resolution
    --plot              \
    --resolution 50m
```

... to repeat the above studies at x4 angular resolution, x4 radial resolution and x4 conservatism then try running something like:

```
python3.10 run.py       \
    -1.0 +50.5 20.0     \
    --duration 11.2     \
    --precision 2500.0  \   # x4 radial resolution
    --conservatism 8.0  \   # x4 conservatism
    --freqLand 384      \
    --freqPlot 16       \
    --freqSimp 16       \
    --nang 33           \   # x4 angular resolution
    --plot              \
    --resolution 50m
```

## Dependencies

GST requires the following Python modules to be installed and available in your `PYTHONPATH`.

* [cartopy](https://pypi.org/project/Cartopy/)
* [geojson](https://pypi.org/project/geojson/)
* [matplotlib](https://pypi.org/project/matplotlib/)
* [numpy](https://pypi.org/project/numpy/)
* [pyguymer3](https://github.com/Guymer/PyGuymer3)
* [shapely](https://pypi.org/project/Shapely/)

GST uses some [Natural Earth](https://www.naturalearthdata.com/) resources via the [Cartopy](https://scitools.org.uk/cartopy/docs/latest/) module. If they do not exist on your system then Cartopy will download them for you in the background. Consequently, a working internet connection may be required the first time you run GST.
