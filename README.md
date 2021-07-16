# Global Sailing Times (GST)

This project aims to show how a vessel sails around the globe.

If you want to run the example script using a profiler and print out the top 25 most time-consuming functions then run:

```
python3.9 -m cProfile -o results.out run.py
python3.9 -c 'import pstats; p = pstats.Stats("results.out"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(25)'
```

## To Do

* make sure that vessels can sail through both the Panama and Suez canals
* use `multiprocessing` in `pyguymer3.geo`
* only buffer (and fill in) the exterior LinearRing of the Polygon that is on water
