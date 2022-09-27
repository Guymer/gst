# Global Sailing Times (GST)

This project aims to show how a vessel sails around the globe.

The `buffer()` function in [PyGuymer3](https://github.com/Guymer/PyGuymer3) has a maximum buffer distance (in one go) of 10,001.5 kilometres. At a speed of 20.0 knots, you will have gone 9,778.56 kilometres in 11 days and 10,667.52 kilometres in 12 days.

## Profiling

If you want to run the example script using a profiler and print out the top 10 most time-consuming functions then run:

```
# for the first time a command is run ...
python3.10 -m cProfile -o first.log run.py -1.0 50.7 20.0 --duration 5.0 > first.out 2> first.err
python3.10 -c 'import pstats; p = pstats.Stats("first.log"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)'

# for the second time a command is run ...
python3.10 -m cProfile -o second.log run.py -1.0 50.7 20.0 --duration 5.0 > second.out 2> second.err
python3.10 -c 'import pstats; p = pstats.Stats("second.log"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)'
```

## Running `compareBufferAngularResolutions.py`

To generate the data needed, it will run commands like:

```
# powers of 2 are 8, 16, 32, ...
python3.10 run.py -1.0 50.7 20.0 --duration 0.09 --nang  9 --precision 10000.0 --resolution 10m
python3.10 run.py -1.0 50.7 20.0 --duration 0.09 --nang 17 --precision 10000.0 --resolution 10m
python3.10 run.py -1.0 50.7 20.0 --duration 0.09 --nang 33 --precision 10000.0 --resolution 10m
...
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80 kilometres.

## Running `compareBufferRadialResolutions.py`

To generate the data needed, it will run commands like:

```
# powers of 2 are 8, 16, 32, ...
python3.10 run.py -1.0 50.7 20.0 --duration 0.09 --nang 513 --precision  5000.0 --resolution 10m
python3.10 run.py -1.0 50.7 20.0 --duration 0.09 --nang 513 --precision 10000.0 --resolution 10m
python3.10 run.py -1.0 50.7 20.0 --duration 0.09 --nang 513 --precision 20000.0 --resolution 10m
...
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80 kilometres.

## Maximum Sailing Distance

To very quickly find out how far a vessel can sail, try running something like:

```
python3.10 run.py       \
    -1.0 50.7 20.0      \   # depart Portsmouth Harbour at 20 knots
    --duration 5.0      \   # approach, but do not cross, The North Pole (20 knots * 5.0 days = 4,444.80 kilometres)
    --precision 40000.0 \   # ~hourly distance steps (20 knots * 1 hour = 37.04 kilometres)
    --conservatism 2.0  \   # some conservatism
    --freqLand 24       \   # ~daily land re-evaluation
    --freqPlot 1        \   # ~hourly plotting
    --freqSimp 1        \   # ~hourly simplification
    --nang 9            \   # minimum number of angles
    --plot              \   # make a plot
    --resolution 110m       # coarsest land resolution (does not have the Panama Canal and Suez Canal)

python3.10 run.py       \
    -1.0 50.7 20.0      \   # depart Portsmouth Harbour at 20 knots
    --duration 11.2     \   # ~maximum distance (20 knots * 11.2 days = 9,956.35 kilometres)
    --precision 40000.0 \   # ~hourly distance steps (20 knots * 1 hour = 37.04 kilometres)
    --conservatism 2.0  \   # some conservatism
    --freqLand 24       \   # ~daily land re-evaluation
    --freqPlot 1        \   # ~hourly plotting
    --freqSimp 1        \   # ~hourly simplification
    --nang 9            \   # minimum number of angles
    --plot              \   # make a plot
    --resolution 50m        # coarsest land resolution (that has the Panama Canal and Suez Canal)
```

... to repeat the above studies at x2 angular resolution, x2 radial resolution and x2 conservatism then try running something like:

```
python3.10 run.py       \
    -1.0 50.7 20.0      \
    --duration 5.0      \
    --precision 20000.0 \   # x2 radial resolution
    --conservatism 4.0  \   # x2 conservatism
    --freqLand 48       \
    --freqPlot 2        \
    --freqSimp 2        \
    --nang 17           \   # x2 angular resolution
    --plot              \
    --resolution 110m

python3.10 run.py       \
    -1.0 50.7 20.0      \
    --duration 11.2     \
    --precision 20000.0 \   # x2 radial resolution
    --conservatism 4.0  \   # x2 conservatism
    --freqLand 48       \
    --freqPlot 2        \
    --freqSimp 2        \
    --nang 17           \   # x2 angular resolution
    --plot              \
    --resolution 50m
```

... to repeat the above studies at x4 angular resolution, x4 radial resolution and x4 conservatism then try running something like:

```
python3.10 run.py       \
    -1.0 50.7 20.0      \
    --duration 5.0      \
    --precision 10000.0 \   # x4 radial resolution
    --conservatism 8.0  \   # x4 conservatism
    --freqLand 96       \
    --freqPlot 4        \
    --freqSimp 4        \
    --nang 33           \   # x4 angular resolution
    --plot              \
    --resolution 110m

python3.10 run.py       \
    -1.0 50.7 20.0      \
    --duration 11.2     \
    --precision 10000.0 \   # x4 radial resolution
    --conservatism 8.0  \   # x4 conservatism
    --freqLand 96       \
    --freqPlot 4        \
    --freqSimp 4        \
    --nang 33           \   # x4 angular resolution
    --plot              \
    --resolution 50m
```

## Dependencies

GST requires the following Python modules to be installed and available in your `PYTHONPATH`.

* [cartopy](https://pypi.org/project/Cartopy/)
* [matplotlib](https://pypi.org/project/matplotlib/)
* [numpy](https://pypi.org/project/numpy/)
* [pyguymer3](https://github.com/Guymer/PyGuymer3)
* [shapely](https://pypi.org/project/Shapely/)

GST uses some [Natural Earth](https://www.naturalearthdata.com/) resources via the [Cartopy](https://scitools.org.uk/cartopy/docs/latest/) module. If they do not exist on your system then Cartopy will download them for you in the background. Consequently, a working internet connection may be required the first time you run GST.
