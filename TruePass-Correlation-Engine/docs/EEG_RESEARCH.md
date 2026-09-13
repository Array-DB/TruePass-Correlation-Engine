# EEG Research Module

Phase 27 implements a read-only research pipeline for consented or synthetic EEG data. It includes validated band-pass filtering and a pluggable **constrained classifier** interface. Outputs are explicitly marked experimental and carry the interpretation `constrained_classifier_output_not_thought_reading`.

TruePass does not implement electrical stimulation, neuromodulation, unrestricted thought reading, or autonomous decisions from EEG. Research hardware/data are optional and remain isolated from the production cybersecurity core.
