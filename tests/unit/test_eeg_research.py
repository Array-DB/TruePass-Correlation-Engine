import numpy as np,pytest
from truepass.research.eeg import EEGResearchPipeline,bandpass
class Classifier:
    def predict(self,samples,sample_rate):return ("rest",.75)
def test_eeg_pipeline_is_constrained():
    t=np.arange(0,2,1/256); x=np.sin(2*np.pi*10*t)
    o=EEGResearchPipeline(Classifier()).analyze(x,sample_rate=256)
    assert o.experimental is True and o.label=="rest" and "not_thought_reading" in o.interpretation
def test_eeg_band_rejects_invalid_nyquist():
    with pytest.raises(ValueError):bandpass(np.ones(100),50,1,40)
