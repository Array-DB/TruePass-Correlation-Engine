# RF Pipeline

Receive-only I/Q sources include synthetic data, replay files, a generic SoapySDR boundary, and HackRF One through SoapySDR/SoapyHackRF when installed.

Pipeline:

`I/Q → window → FFT → PSD/spectrogram → RF feature vector → baseline → anomaly/clustering → canonical event → correlation`

Supported deterministic windows include Hann, Blackman, and boxcar. RF features include power/noise-floor measurements, occupied bandwidth, spectral entropy/centroid/flatness, drift, duty cycle, and burst descriptors.

An RF anomaly is a measurable departure from a baseline, not proof of compromise or human intent. HackRF support is receive-only and TruePass exposes no TX stream API.
