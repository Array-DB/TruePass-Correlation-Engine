"""Hardware-independent SDR sources with receive-only HackRF One support."""

from __future__ import annotations

import importlib
import math
import random
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class SDRConfig:
    sample_rate: float = 2_000_000.0
    center_frequency: float = 100_000_000.0
    gain: float = 0.0
    buffer_size: int = 4096
    device: str = "synthetic"

    def __post_init__(self) -> None:
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if self.center_frequency < 0:
            raise ValueError("center_frequency must be non-negative")
        if self.buffer_size < 2:
            raise ValueError("buffer_size must be at least 2")
        if not math.isfinite(self.gain):
            raise ValueError("gain must be finite")


@dataclass(frozen=True, slots=True)
class SDRStatus:
    driver: str
    label: str
    serial: str | None
    open: bool
    samples_read: int
    sample_rate: float
    center_frequency: float
    gain: float


class SDRSource(Protocol):
    config: SDRConfig

    def read_samples(self, count: int | None = None) -> list[complex]: ...


class SyntheticIQSource:
    def __init__(
        self,
        config: SDRConfig | None = None,
        *,
        tone_hz: float = 100_000.0,
        noise_amplitude: float = 0.02,
        seed: int = 0,
    ) -> None:
        self.config = config or SDRConfig()
        self.tone_hz = tone_hz
        self.noise_amplitude = noise_amplitude
        self._phase = 0
        self._rng = random.Random(seed)

    def read_samples(self, count: int | None = None) -> list[complex]:
        n = count or self.config.buffer_size
        if n <= 0:
            raise ValueError("sample count must be positive")
        out: list[complex] = []
        for index in range(n):
            phase = 2 * math.pi * self.tone_hz * (self._phase + index) / self.config.sample_rate
            noise = complex(
                self._rng.uniform(-self.noise_amplitude, self.noise_amplitude),
                self._rng.uniform(-self.noise_amplitude, self.noise_amplitude),
            )
            out.append(complex(math.cos(phase), math.sin(phase)) + noise)
        self._phase += n
        return out


class FileIQSource:
    """Sequential little-endian float32 I/Q replay source."""

    def __init__(self, path: str | Path, config: SDRConfig | None = None) -> None:
        self.path = Path(path)
        self.config = config or SDRConfig(device="file")
        self._handle = self.path.open("rb")
        self._closed = False

    def read_samples(self, count: int | None = None) -> list[complex]:
        if self._closed:
            raise RuntimeError("file I/Q source is closed")
        n = count or self.config.buffer_size
        if n <= 0:
            raise ValueError("sample count must be positive")
        raw = self._handle.read(n * 8)
        complete_length = len(raw) - (len(raw) % 8)
        return [complex(i_value, q_value) for i_value, q_value in struct.iter_unpack("<ff", raw[:complete_length])]

    def rewind(self) -> None:
        if self._closed:
            raise RuntimeError("file I/Q source is closed")
        self._handle.seek(0)

    def close(self) -> None:
        if not self._closed:
            self._handle.close()
            self._closed = True

    def __enter__(self) -> "FileIQSource":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


@dataclass(frozen=True, slots=True)
class SDRDeviceInfo:
    driver: str
    label: str
    serial: str | None
    raw: dict[str, str]


class RealSoapySDRSource:
    """Generic receive-only SoapySDR CF32 source.

    The adapter intentionally exposes no transmit path. It is suitable for
    HackRF One and other SoapySDR devices with a receive channel.
    """

    def __init__(
        self,
        config: SDRConfig | None = None,
        *,
        device_args: Any | None = None,
    ) -> None:
        self.config = config or SDRConfig(device="soapy")
        try:
            self._soapy = importlib.import_module("SoapySDR")
        except ImportError as exc:
            raise RuntimeError("SoapySDR Python bindings are not installed") from exc

        # Keep the original SoapySDRKwargs object when one came directly from
        # Device.enumerate().  Some hardware drivers (and some HackRF clones)
        # will enumerate with a generic driver query but will not open again
        # from a reconstructed {driver: ...} dictionary.  Soapy's enumerated
        # descriptor is the authoritative set of make() arguments.
        device_selector = device_args if device_args is not None else {}
        try:
            args = {str(key): str(value) for key, value in dict(device_selector).items()}
        except Exception:
            args = {}
        self._device = self._soapy.Device(device_selector)
        rx = self._soapy.SOAPY_SDR_RX
        self._device.setSampleRate(rx, 0, self.config.sample_rate)
        self._device.setFrequency(rx, 0, self.config.center_frequency)
        self._device.setGain(rx, 0, self.config.gain)
        self._stream = self._device.setupStream(rx, self._soapy.SOAPY_SDR_CF32, [0])
        self._device.activateStream(self._stream)
        self._closed = False
        self._samples_read = 0
        self._driver = str(args.get("driver", "soapy"))
        self._serial = args.get("serial")

    @property
    def status(self) -> SDRStatus:
        return SDRStatus(
            driver=self._driver,
            label=self.config.device,
            serial=self._serial,
            open=not self._closed,
            samples_read=self._samples_read,
            sample_rate=self.config.sample_rate,
            center_frequency=self.config.center_frequency,
            gain=self.config.gain,
        )

    def read_samples(self, count: int | None = None) -> list[complex]:
        if self._closed:
            raise RuntimeError("SDR source is closed")
        import numpy as np

        n = count or self.config.buffer_size
        if n <= 0:
            raise ValueError("sample count must be positive")
        buffer = np.empty(n, dtype=np.complex64)
        result = self._device.readStream(self._stream, [buffer], n, timeoutUs=1_000_000)
        if result.ret < 0:
            raise RuntimeError(f"SoapySDR readStream failed: {result.ret}")
        if result.ret == 0:
            return []
        self._samples_read += int(result.ret)
        return [complex(value) for value in buffer[: result.ret]]

    def close(self) -> None:
        if self._closed:
            return
        try:
            self._device.deactivateStream(self._stream)
        finally:
            try:
                self._device.closeStream(self._stream)
            finally:
                self._closed = True

    def __enter__(self) -> "RealSoapySDRSource":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @classmethod
    def enumerate(cls, driver: str | None = None) -> tuple[SDRDeviceInfo, ...]:
        try:
            soapy = importlib.import_module("SoapySDR")
        except ImportError:
            return ()
        query = {} if driver is None else {"driver": driver}
        out: list[SDRDeviceInfo] = []
        try:
            enumerated = soapy.Device.enumerate(query)
        except Exception:
            return ()
        for item in enumerated:
            raw = {str(key): str(value) for key, value in dict(item).items()}
            out.append(
                SDRDeviceInfo(
                    raw.get("driver", "unknown"),
                    raw.get("label", raw.get("device", "SDR")),
                    raw.get("serial"),
                    raw,
                )
            )
        return tuple(out)


class HackRFOneSource(RealSoapySDRSource):
    """Receive-only HackRF One adapter using the SoapyHackRF driver."""

    MIN_FREQUENCY_HZ = 1_000_000.0
    MAX_FREQUENCY_HZ = 6_000_000_000.0

    def __init__(self, config: SDRConfig | None = None, *, serial: str | None = None) -> None:
        cfg = config or SDRConfig(device="hackrf")
        if not self.MIN_FREQUENCY_HZ <= cfg.center_frequency <= self.MAX_FREQUENCY_HZ:
            raise ValueError("HackRF One center frequency must be between 1 MHz and 6 GHz")

        try:
            soapy = importlib.import_module("SoapySDR")
        except ImportError as exc:
            raise RuntimeError("SoapySDR Python bindings are not installed") from exc

        try:
            enumerated = tuple(soapy.Device.enumerate({"driver": "hackrf"}))
        except Exception as exc:
            raise RuntimeError(f"HackRF enumeration failed: {exc}") from exc
        if not enumerated:
            raise RuntimeError("no HackerRF One enumerated through SoapySDR/SoapyHackRF")

        selected = None
        if serial:
            wanted = str(serial).strip().lower()
            for candidate in enumerated:
                raw = {str(k): str(v) for k, v in dict(candidate).items()}
                candidate_serial = raw.get("serial", "").strip().lower()
                if candidate_serial == wanted or candidate_serial.endswith(wanted) or wanted.endswith(candidate_serial):
                    selected = candidate
                    break
            if selected is None:
                available = [str(dict(d).get("serial", "unknown")) for d in enumerated]
                raise RuntimeError(
                    f"requested HackRF serial {serial!r} was not found; available serials: {available}"
                )
        else:
            selected = enumerated[0]

        # Pass the exact enumerated SoapySDRKwargs object into Device.make().
        # This is more robust than reconstructing only driver/serial fields.
        super().__init__(cfg, device_args=selected)

    @classmethod
    def enumerate_devices(cls) -> tuple[SDRDeviceInfo, ...]:
        return cls.enumerate("hackrf")


def open_sdr_source(
    config: SDRConfig,
    *,
    serial: str | None = None,
    file_path: str | Path | None = None,
) -> SDRSource:
    """Open a configured receive source through a common factory."""

    device = config.device.lower().strip()
    if device == "synthetic":
        return SyntheticIQSource(config)
    if device in {"hackrf", "hackrfone", "hackrf-one"}:
        return HackRFOneSource(config, serial=serial)
    if device == "file":
        if file_path is None:
            raise ValueError("file_path is required for the file SDR source")
        return FileIQSource(file_path, config)
    if device in {"soapy", "soapysdr"}:
        return RealSoapySDRSource(config)
    raise ValueError(f"unsupported SDR source: {config.device}")
