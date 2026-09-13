import pytest
from truepass.research.voice import VoiceResearchPipeline
class STT:
    def transcribe(self,pcm,sample_rate):return ("status report",.9)
class Intent:
    def classify(self,text):return ("query_status",.8)
def test_voice_pipeline_is_experimental_and_bounded():
    o=VoiceResearchPipeline(STT(),Intent()).analyze(b"1234",sample_rate=16000)
    assert o.experimental is True and o.intent=="query_status" and o.confidence==pytest.approx(.72)
def test_voice_rejects_empty_audio():
    with pytest.raises(ValueError):VoiceResearchPipeline(STT(),Intent()).analyze(b"",sample_rate=16000)
