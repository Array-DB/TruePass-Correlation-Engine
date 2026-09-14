import pytest
from truepass.sdr.sources import HackRFOneSource,SDRConfig

def test_hackrf_frequency_guard_runs_without_hardware():
    with pytest.raises(ValueError):HackRFOneSource(SDRConfig(center_frequency=100_000.0,device='hackrf'))

def test_hackrf_enumeration_gracefully_empty_without_soapy():
    devices=HackRFOneSource.enumerate_devices()
    assert isinstance(devices,tuple)


def test_hackrf_opens_exact_enumerated_descriptor(monkeypatch):
    import truepass.sdr.sources as sources

    class Descriptor(dict):
        pass

    descriptor = Descriptor(driver='hackrf', serial='ABC123', label='HackRF One #0')

    class FakeDeviceInstance:
        def setSampleRate(self, *args): pass
        def setFrequency(self, *args): pass
        def setGain(self, *args): pass
        def setupStream(self, *args): return object()
        def activateStream(self, *args): pass
        def deactivateStream(self, *args): pass
        def closeStream(self, *args): pass

    class FakeDeviceFactory:
        opened_with = None
        @staticmethod
        def enumerate(query):
            assert query == {'driver': 'hackrf'}
            return (descriptor,)
        def __new__(cls, args):
            cls.opened_with = args
            assert args is descriptor
            return FakeDeviceInstance()

    class FakeSoapy:
        Device = FakeDeviceFactory
        SOAPY_SDR_RX = 1
        SOAPY_SDR_CF32 = 'CF32'

    real_import = sources.importlib.import_module
    def fake_import(name):
        if name == 'SoapySDR':
            return FakeSoapy
        return real_import(name)

    monkeypatch.setattr(sources.importlib, 'import_module', fake_import)
    cfg = sources.SDRConfig(device='hackrf', center_frequency=100_000_000.0)
    with sources.HackRFOneSource(cfg, serial='ABC123'):
        pass
    assert FakeDeviceFactory.opened_with is descriptor
