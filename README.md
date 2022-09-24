# Global Sailing Times (GST)

This project aims to show how a vessel sails around the globe.

The `buffer()` function in [PyGuymer3](https://github.com/Guymer/PyGuymer3) has a maximum buffer distance (in one go) of 10,001.5 kilometres. At a speed of 20.0 knots, you will have gone
9,778.56 kilometres in 11 days and 10,667.52 kilometres in 12 days.

## Profiling

If you want to run the example script using a profiler and print out the top 10 most time-consuming functions then run:

```
# for the first time a command is run ...
python3.10 -m cProfile -o first.log run.py -1.0 50.7 20.0 --dur 4.0 --nang 33 --res 110m > first.out 2> first.err
python3.10 -c 'import pstats; p = pstats.Stats("first.log"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)'

# for the second time a command is run ...
python3.10 -m cProfile -o second.log run.py -1.0 50.7 20.0 --dur 4.0 --nang 33 --res 110m > second.out 2> second.err
python3.10 -c 'import pstats; p = pstats.Stats("second.log"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)'
```

## Running `compareBufferAngularResolutions.py`

To generate the data needed by `compareBufferAngularResolutions.py`, it will run commands like:

```
# powers of 2 are 8, 16, 32, 64, 128, 256, 512
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang   9 --prec 10000.0 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang  17 --prec 10000.0 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang  33 --prec 10000.0 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang  65 --prec 10000.0 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 129 --prec 10000.0 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 257 --prec 10000.0 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 513 --prec 10000.0 --res 10m
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80 kilometres.

## Running `resolutionConvergence.py`

To generate the data needed by `resolutionConvergence.py` run:

```
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 9 --res 110m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 9 --res 50m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 9 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 13 --res 110m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 13 --res 50m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 13 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 17 --res 110m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 17 --res 50m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 17 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 37 --res 110m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 37 --res 50m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 37 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 89 --res 110m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 89 --res 50m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 89 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 181 --res 110m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 181 --res 50m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 181 --res 10m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 361 --res 110m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 361 --res 50m
python3.10 run.py -1.0 50.7 20.0 --dur 0.09 --nang 361 --res 10m
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80 kilometres.

`run.py` is very slow for large values of `nang`.

## Maximum Sailing Distance

To very quickly find out how far a vessel can sail, try running:

```
python3.10 run.py -1.0 50.7 20.0 --dur 2.0 --nang 9 --res 110m
```

## Dependencies

GST requires the following Python modules to be installed and available in your `PYTHONPATH`.

* [cartopy](https://pypi.org/project/Cartopy/)
* [matplotlib](https://pypi.org/project/matplotlib/)
* [numpy](https://pypi.org/project/numpy/)
* [pyguymer3](https://github.com/Guymer/PyGuymer3)
* [shapely](https://pypi.org/project/Shapely/)

GST uses some [Natural Earth](https://www.naturalearthdata.com/) resources via the [Cartopy](https://scitools.org.uk/cartopy/docs/latest/) module. If they do not exist on your system then Cartopy will download them for you in the background. Consequently, a working internet connection may be required the first time you run GST.

## To Do

* make sure that vessels can sail through both the Panama and Suez canals
