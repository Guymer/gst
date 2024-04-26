#!/usr/bin/env bash

# Check that non-standard programs are installed. "standard" programs are
# anything that is specified in the POSIX.1-2008 standard (and the IEEE Std
# 1003.1 standard) or that is a BASH builtin command. Therefore, "non-standard"
# programs are anything that does not appear on the following two lists:
#   * https://pubs.opengroup.org/onlinepubs/9699919799/idx/utilities.html
#   * https://www.gnu.org/software/bash/manual/html_node/Bash-Builtins.html

# Loop over resolutions ...
for res in "c" "l" "i" "h" "f"; do
    # Run GST (for README.md) ...
    python3.11 run.py +18.079 +59.324 20.0 --duration 0.03 --freqLand 3000 --freqPlot 10 --local --nang 33 --plot --precision 10.0 --resolution "${res}"

    # Run GST (for compareBufferAngularResolutions.py) ...
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nang 9 --plot --precision 1250.0 --resolution "${res}"
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nang 17 --plot --precision 1250.0 --resolution "${res}"
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nang 33 --plot --precision 1250.0 --resolution "${res}"
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nang 65 --plot --precision 1250.0 --resolution "${res}"
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nang 129 --plot --precision 1250.0 --resolution "${res}"
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 1 --freqSimp 768 --local --nang 257 --plot --precision 1250.0 --resolution "${res}"

    # Run GST (for compareBufferRadialResolutions.py) ...
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 1536 --freqPlot 16 --freqSimp 1536 --local --nang 257 --plot --precision 625.0 --resolution "${res}"
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 768 --freqPlot 8 --freqSimp 768 --local --nang 257 --plot --precision 1250.0 --resolution "${res}"
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 384 --freqPlot 4 --freqSimp 384 --local --nang 257 --plot --precision 2500.0 --resolution "${res}"
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 192 --freqPlot 2 --freqSimp 192 --local --nang 257 --plot --precision 5000.0 --resolution "${res}"
    python3.11 run.py -1.0 +50.5 20.0 --duration 0.09 --freqLand 96 --freqPlot 1 --freqSimp 96 --local --nang 257 --plot --precision 10000.0 --resolution "${res}"

    # Run GST (for complexity.py) ...
    python3.11 run.py 0.0 0.0 20.0 --conservatism 2.0 --duration 0.01 --freqLand 192 --freqSimp 8 --nang 9 --precision 5000.0 --resolution "${res}"
    python3.11 run.py 0.0 0.0 20.0 --conservatism 2.0 --duration 0.01 --freqLand 384 --freqSimp 16 --nang 17 --precision 2500.0 --resolution "${res}"
    python3.11 run.py 0.0 0.0 20.0 --conservatism 2.0 --duration 0.01 --freqLand 768 --freqSimp 32 --nang 33 --precision 1250.0 --resolution "${res}"

    # Run GST (for showNarrowPassages.py) ...
    python3.11 run.py 0.0 0.0 20.0 --duration 0.01 --freqLand 192 --freqSimp 8 --nang 9 --precision 5000.0 --resolution "${res}"
    python3.11 run.py 0.0 0.0 20.0 --duration 0.01 --freqLand 384 --freqSimp 16 --nang 17 --precision 2500.0 --resolution "${res}"
    python3.11 run.py 0.0 0.0 20.0 --duration 0.01 --freqLand 768 --freqSimp 32 --nang 33 --precision 1250.0 --resolution "${res}"
done

# ******************************************************************************

# Loop over days ...
for dur in {1..24}; do
    # Run GST (for ripples.py) ...
    python3.11 run.py -1.0 +50.5 20.0 --conservatism 2.0 --duration ${dur}.0 --freqLand 192 --freqPlot 8 --freqSimp 8 --nang 9 --plot --precision 5000.0 --resolution i
    python3.11 run.py -1.0 +50.5 20.0 --conservatism 2.0 --duration ${dur}.0 --freqLand 384 --freqPlot 16 --freqSimp 16 --nang 17 --plot --precision 2500.0 --resolution i
    python3.11 run.py -1.0 +50.5 20.0 --conservatism 2.0 --duration ${dur}.0 --freqLand 768 --freqPlot 32 --freqSimp 32 --nang 33 --plot --precision 1250.0 --resolution i
done
