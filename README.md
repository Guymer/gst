# Global Sailing Times (GST)

This project aims to show have a vessel sails around the globe.

If you want to run the example script using a profiler and print out the top 25 most time-consuming functions then run:

```
python3.9 -m cProfile -o results.out run.py
python3.9 -c 'import pstats; p = pstats.Stats("results.out"); p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(25)'
```
