# HackRF One compatibility

TruePass supports HackRF One as an **RX-only sensor** through SoapySDR + SoapyHackRF. No transmit stream is created anywhere in the integration.

## Linux prerequisites

Install the HackRF host tools/libhackrf, SoapySDR, its Python bindings, and the SoapyHackRF module using your distribution or conda-forge packages. Confirm the system driver independently with `hackrf_info` and `SoapySDRUtil --find="driver=hackrf"`.

The TruePass adapter uses the SoapySDR device selector `driver=hackrf` and optionally a serial number. HackRF One is validated for center frequencies from 1 MHz through 6 GHz, matching the published hardware range.

## Receive smoke test

```bash
truepass collect sdr-hackrf --samples 4096
```

Configure sample rate, center frequency, gain and buffer size in `config/truepass.toml` before capture. The command prints complex IQ samples and exits. It never transmits.

## Hardware-free development

Use `truepass collect sdr-synthetic` or `FileIQSource` when HackRF hardware or SoapySDR is unavailable. `truepass doctor` reports discovered HackRF devices when the SoapyHackRF plugin is present.

References:
- Great Scott Gadgets HackRF documentation: https://hackrf.readthedocs.io/
- SoapyHackRF: https://github.com/pothosware/SoapyHackRF

## Remediation Phase 5/6 smoke path

The receive path can now be exercised through the shared DSP pipeline without a GUI:

```bash
truepass collect sdr-spectrum --source hackrf --samples 4096
```

The command returns a bounded JSON DSP frame containing frequency bins, FFT magnitude,
PSD, waterfall data, and RF features. This is the backend payload foundation for the
later `/ws/spectrum` live dashboard phase; the WebSocket/UI connection is not yet
claimed complete.
