# ADR 0004 — RF anomaly and clustering semantics

## Status
Accepted.

## Context
TruePass must discover unusual RF observations without converting statistical novelty into a security conclusion. X-means-style adaptive clustering is useful for discovering structure, but a new cluster can result from legitimate devices, propagation changes, sensor changes, or previously unseen normal activity.

## Decision
TruePass treats anomaly and clustering outputs as **observations requiring correlation**. Statistical-distance and Isolation Forest outputs include model identifiers and human-readable reasons. DBSCAN noise points and adaptive K-means clusters never receive attacker labels. Adaptive K-means with a BIC-style model-selection criterion is used as the initial X-means-compatible strategy to avoid an unnecessary unmaintained dependency.

## Consequences
Phase 15 must combine RF novelty with independent time, host, process, network, device, identity, and sensor-reliability evidence before an incident candidate can be raised. Scores remain explainable and do not imply causation.
