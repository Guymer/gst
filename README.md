# Global Sailing Times (GST)

This project aims to show how a vessel sails around the globe.

If you want to run the example script using a profiler and print out the top 25 most time-consuming functions then run:

```
python3.9 -m cProfile -o results.out run.py -1.0 50.7 20.0 --dur 0.09
python3.9 -c 'import pstats; p = pstats.Stats("results.out"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(25)'
```

## `compareBufferResolutions.py`

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

`run.py` is very slow for large values of `nang`. Try running only the first three lines and then run `compareBufferResolutions.py` to see what the benefit is. You can then run the remaining lines one-by-one and re-run `compareBufferResolutions.py` to see what the improvements are. You may come to the conclusion that it is not worth running `--nang 361`.

## `resolutionConvergence.py`

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

## To Do

* make sure that vessels can sail through both the Panama and Suez canals
* only buffer (and fill in) the exterior LinearRing of the Polygon that is on water
