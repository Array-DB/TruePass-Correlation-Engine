import pytest
from truepass.sdr.sources import HackRFOneSource,SDRConfig

def test_hackrf_frequency_guard_runs_without_hardware():
    with pytest.raises(ValueError):HackRFOneSource(SDRConfig(center_frequency=100_000.0,device='hackrf'))

def test_hackrf_enumeration_gracefully_empty_without_soapy():
    devices=HackRFOneSource.enumerate_devices()
    assert isinstance(devices,tuple)
