"""Constrained, non-stimulation EEG research preprocessing and classification."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
import numpy as np
from scipy.signal import butter, sosfiltfilt

@dataclass(frozen=True, slots=True)
class EEGObservation:
    label: str
    confidence: float
    channels: int
    samples: int
    experimental: bool = True
    interpretation: str = "constrained_classifier_output_not_thought_reading"

class EEGClassifier(Protocol):
    def predict(self, samples: np.ndarray, sample_rate: float) -> tuple[str,float]: ...

def bandpass(samples: np.ndarray, sample_rate: float, low_hz: float=1.0, high_hz: float=40.0) -> np.ndarray:
    x=np.asarray(samples,dtype=np.float64)
    if x.ndim not in (1,2): raise ValueError("samples must be 1-D or 2-D")
    if sample_rate <= 0 or not 0 < low_hz < high_hz < sample_rate/2: raise ValueError("invalid EEG band/sample rate")
    sos=butter(4,[low_hz,high_hz],btype="bandpass",fs=sample_rate,output="sos")
    return sosfiltfilt(sos,x,axis=-1)

class EEGResearchPipeline:
    def __init__(self,classifier: EEGClassifier) -> None:self._classifier=classifier
    def analyze(self,samples: np.ndarray,*,sample_rate: float) -> EEGObservation:
        filtered=bandpass(samples,sample_rate)
        label,confidence=self._classifier.predict(filtered,sample_rate)
        channels=1 if filtered.ndim==1 else filtered.shape[0]
        return EEGObservation(label,max(0.0,min(1.0,float(confidence))),channels,filtered.shape[-1])
