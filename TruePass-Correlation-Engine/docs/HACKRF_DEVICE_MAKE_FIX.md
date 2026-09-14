# HackerRF Device.make compatibility fix

This build opens HackerRF hardware using the exact `SoapySDRKwargs` descriptor returned by `SoapySDR.Device.enumerate({"driver": "hackrf"})` rather than reconstructing a minimal `{driver, serial}` dictionary. This improves compatibility with SoapyHackRF devices that enumerate successfully but reject a generic `Device.make()` selector.

On Linux, the local installer also exposes the system Python `SoapySDR` package to the TruePass virtual environment when a matching system binding is installed (common on Arch/Manjaro), without enabling all system site-packages.
