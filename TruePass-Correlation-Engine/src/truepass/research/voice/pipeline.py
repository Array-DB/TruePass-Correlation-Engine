"""Isolated Voice/Echo research pipeline interfaces.

This module produces research observations only. Voice alone is never sufficient proof of identity.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

class VoiceStage(StrEnum):
    VAD="vad"; STT="speech_to_text"; NLP="nlp"; INTENT="intent"; POLICY="policy"; TTS="text_to_speech"

@dataclass(frozen=True, slots=True)
class VoiceObservation:
    transcript: str
    intent: str | None
    confidence: float
    replay_risk: float | None = None
    synthetic_voice_risk: float | None = None
    experimental: bool = True

class SpeechToText(Protocol):
    def transcribe(self, pcm: bytes, sample_rate: int) -> tuple[str, float]: ...

class IntentClassifier(Protocol):
    def classify(self, text: str) -> tuple[str, float]: ...

class VoiceResearchPipeline:
    def __init__(self, stt: SpeechToText, intent: IntentClassifier) -> None:
        self._stt=stt; self._intent=intent
    def analyze(self, pcm: bytes, *, sample_rate: int) -> VoiceObservation:
        if sample_rate <= 0: raise ValueError("sample_rate must be positive")
        if not pcm: raise ValueError("pcm must not be empty")
        text, stt_conf = self._stt.transcribe(pcm, sample_rate)
        label, intent_conf = self._intent.classify(text)
        confidence=max(0.0,min(1.0,stt_conf*intent_conf))
        return VoiceObservation(text,label,confidence)
