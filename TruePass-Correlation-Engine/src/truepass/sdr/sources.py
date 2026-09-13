"""Hardware-independent SDR sources with optional receive-only HackRF One support."""
from __future__ import annotations
import importlib, math, random, struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

@dataclass(frozen=True,slots=True)
class SDRConfig:
    sample_rate:float=2_000_000.0
    center_frequency:float=100_000_000.0
    gain:float=0.0
    buffer_size:int=4096
    device:str="synthetic"

class SDRSource(Protocol):
    config:SDRConfig
    def read_samples(self,count:int|None=None)->list[complex]: ...

class SyntheticIQSource:
    def __init__(self,config:SDRConfig|None=None,*,tone_hz:float=100_000.0,noise_amplitude:float=0.02,seed:int=0)->None:
        self.config=config or SDRConfig();self.tone_hz=tone_hz;self.noise_amplitude=noise_amplitude;self._phase=0;self._rng=random.Random(seed)
    def read_samples(self,count:int|None=None)->list[complex]:
        n=count or self.config.buffer_size; out=[]
        for i in range(n):
            phase=2*math.pi*self.tone_hz*(self._phase+i)/self.config.sample_rate
            noise=complex(self._rng.uniform(-self.noise_amplitude,self.noise_amplitude),self._rng.uniform(-self.noise_amplitude,self.noise_amplitude))
            out.append(complex(math.cos(phase),math.sin(phase))+noise)
        self._phase+=n; return out

class FileIQSource:
    def __init__(self,path:str|Path,config:SDRConfig|None=None)->None:self.path=Path(path);self.config=config or SDRConfig(device="file")
    def read_samples(self,count:int|None=None)->list[complex]:
        n=count or self.config.buffer_size; raw=self.path.read_bytes()[:n*8]; out=[]
        for i,q in struct.iter_unpack("<ff",raw):out.append(complex(i,q))
        return out

@dataclass(frozen=True, slots=True)
class SDRDeviceInfo:
    driver:str
    label:str
    serial:str|None
    raw:dict[str,str]

class RealSoapySDRSource:
    """Generic receive-only SoapySDR CF32 source.

    This class deliberately never creates a TX stream. It is suitable for HackRF
    One and other SoapySDR devices that expose an RX channel.
    """
    def __init__(self,config:SDRConfig|None=None,*,device_args:dict[str,str]|None=None)->None:
        self.config=config or SDRConfig(device="soapy")
        try:self._soapy=importlib.import_module("SoapySDR")
        except ImportError as exc:raise RuntimeError("SoapySDR Python bindings are not installed") from exc
        args=dict(device_args or {})
        self._device=self._soapy.Device(args)
        rx=self._soapy.SOAPY_SDR_RX
        self._device.setSampleRate(rx,0,self.config.sample_rate)
        self._device.setFrequency(rx,0,self.config.center_frequency)
        if self.config.gain is not None:self._device.setGain(rx,0,self.config.gain)
        self._stream=self._device.setupStream(rx,self._soapy.SOAPY_SDR_CF32,[0])
        self._device.activateStream(self._stream)
        self._closed=False
    def read_samples(self,count:int|None=None)->list[complex]:
        import numpy as np
        n=count or self.config.buffer_size;buf=np.empty(n,dtype=np.complex64)
        result=self._device.readStream(self._stream,[buf],n)
        if result.ret<0:raise RuntimeError(f"SoapySDR readStream failed: {result.ret}")
        return [complex(x) for x in buf[:result.ret]]
    def close(self)->None:
        if self._closed:return
        self._device.deactivateStream(self._stream);self._device.closeStream(self._stream);self._closed=True
    def __enter__(self)->"RealSoapySDRSource":return self
    def __exit__(self,*_:object)->None:self.close()
    @classmethod
    def enumerate(cls,driver:str|None=None)->tuple[SDRDeviceInfo,...]:
        try:soapy=importlib.import_module("SoapySDR")
        except ImportError:return ()
        query={} if driver is None else {"driver":driver};out=[]
        for item in soapy.Device.enumerate(query):
            raw={str(k):str(v) for k,v in dict(item).items()};out.append(SDRDeviceInfo(raw.get("driver","unknown"),raw.get("label",raw.get("device","SDR")),raw.get("serial"),raw))
        return tuple(out)

class HackRFOneSource(RealSoapySDRSource):
    """Receive-only HackRF One adapter using the SoapyHackRF driver."""
    MIN_FREQUENCY_HZ=1_000_000.0
    MAX_FREQUENCY_HZ=6_000_000_000.0
    def __init__(self,config:SDRConfig|None=None,*,serial:str|None=None)->None:
        cfg=config or SDRConfig(device="hackrf")
        if not self.MIN_FREQUENCY_HZ<=cfg.center_frequency<=self.MAX_FREQUENCY_HZ:raise ValueError("HackRF One center frequency must be between 1 MHz and 6 GHz")
        args={"driver":"hackrf"}
        if serial:args["serial"]=serial
        super().__init__(cfg,device_args=args)
    @classmethod
    def enumerate_devices(cls)->tuple[SDRDeviceInfo,...]:return cls.enumerate("hackrf")
