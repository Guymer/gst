# Global Sailing Times (GST)

This project aims to show how a vessel sails around the globe.

## Profiling

If you want to run the example script using a profiler and print out the top 25 most time-consuming functions then run:

```
python3.9 -m cProfile -o results.out run.py -1.0 50.7 20.0 --dur 0.09
python3.9 -c 'import pstats; p = pstats.Stats("results.out"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(25)'
```

## Running `compareBufferResolutions.py`

To generate the data needed by `compareBufferResolutions.py` run:

```
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 10 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 19 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 37 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 91 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 181 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 361 --res 10m
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80km.

`run.py` is very slow for large values of `nang`. Try running only the first couple of lines and then run `compareBufferResolutions.py` to see what the benefit is. You can then run the remaining lines one-by-one and re-run `compareBufferResolutions.py` to see what the improvements are. You may come to the conclusion that it is not worth running `--nang 181` or `--nang 361`.

## Running `resolutionConvergence.py`

To generate the data needed by `resolutionConvergence.py` run:

```
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 10 --res 110m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 10 --res 50m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 10 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 19 --res 110m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 19 --res 50m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 19 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 37 --res 110m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 37 --res 50m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 37 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 91 --res 110m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 91 --res 50m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 91 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 181 --res 110m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 181 --res 50m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 181 --res 10m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 361 --res 110m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 361 --res 50m
python3.9 run.py -1.0 50.7 20.0 --dur 0.09 --nang 361 --res 10m
```

After sailing for 0.09 days at 20.0 knots a vessel will have gone 80,006.4 metres, which I'll round to 80km.

`run.py` is very slow for large values of `nang`.

## Maximum Sailing Distance

To very quickly find out how far a vessel can sail, try running:

```
python3.9 run.py -1.0 50.7 20.0 --dur 2.0
```

## Dependencies

GST requires the following Python modules to be installed and available in your `PYTHONPATH`.

* [cartopy](https://pypi.org/project/Cartopy/)
* [matplotlib](https://pypi.org/project/matplotlib/)
* [numpy](https://pypi.org/project/numpy/)
* [pyguymer3](https://github.com/Guymer/PyGuymer3)
* [shapely](https://pypi.org/project/Shapely/)

GST uses some [Natural Earth](https://www.naturalearthdata.com/) resources via the [Cartopy](https://scitools.org.uk/cartopy/docs/latest/) module. If they do not exist on your system then Cartopy will download them for you in the background. Consequently, a working internet connection may be required the first time you run GST.

## Bugs

* Determining the maximum sailing Polygon breaks between `python3.9 run.py -1.0 50.7 20.0 --dur 4.93 --nang 37 --plot --freqPlot 200` and `python3.9 run.py -1.0 50.7 20.0 --dur 4.94 --nang 37 --plot --freqPlot 200` (which is between 4,382.57km and 4,391.46km)
* `python3.9 run.py -1.0 50.7 20.0 --dur 5.0 --nang 37 --plot --freqPlot 200` and Svalbard
* `python3.9 run.py -1.0 50.7 20.0 --dur 6.0 --nang 37 --plot --freqPlot 200` and Greenland

## To Do

* make sure that vessels can sail through both the Panama and Suez canals
