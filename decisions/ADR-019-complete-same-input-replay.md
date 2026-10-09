# ADR-019 — Complete training-only PLACEHOLDER Conv/BatchNorm replay

Date: 2026-10-10

Status: Accepted (autopilot) — pending human review

## Context

ADR-018's joint stem/BN substitution still fails the unchanged ADR-011 budgets.
ADR-015 and ADR-016 replay only two Conv/BN pairs. Their local measurements cannot
explain the residual arithmetic across all 53 saved Conv and 34 BatchNorm nodes.
The selected saved baseline remains the reference; all failed exports remain
rejected, and ADR-012's labelled toy diagnostic workaround remains in force.

## Decision — declared before execution

Extend the guarded replay pipeline to **every** saved Conv2d and BatchNorm2d,
selected by module order and parameter-name matching, independently of errors.
Require a one-to-one match with every Conv/BN graph node; validate saved parameter
bits and Conv geometry/BN epsilon and inference mode, including Identity aliases.
Replay each native operator on both its exact Python and tapped preserved-ORT
input. Keep the saved Python pre-activation capture, with copying before in-place
timm activations. Report Python and ORT replay fidelity, local kernel and
propagation differences and original/tapped logit agreement for every operator.

For all BNs retain the three ADR-015 primitive expressions and the rounded
float64 diagnostic, and measure both ADR-016 promoted affine recipes. No promoted
Conv replacement is part of this complete replay. Audit isolated serialized and
actual disabled-runtime native operators against saved parameters/attributes;
audit both promoted BN expressions and constant bits in actual runtime graphs.

Report signed elementwise accounting with four distinct terms: Python replay
fidelity, propagation through the Python operator, same-input ORT kernel drift,
and extracted-versus-whole-graph execution drift. Compute each term and the total
in float64, check the telescoping identity, and retain per-term signed extrema
and means. Separate maxima cannot be added as an exact worst-case decomposition.
Track complete aggregates and hashes only; ordered rows and graph copies stay
ignored under data/. Verify aggregate reconstruction and every graph checksum.

Use all and only the existing ordered training component index images, unchanged
saved model/state/fits/preprocessing and CPU sequential/two intra-op/one inter-op
profile. Verify retained exports and valid preserved evidence before inference.
No frozen test/held-out/stress inference, quantisation fit, retraining, reference
or budget change, favourable layer subset, or deployment selection. Every graph
and result is **PLACEHOLDER diagnostic, never bundle**. Exit 0 means evidence
was written; M4 remains incomplete regardless of diagnostic differences.

## Consequences

This complete accounting can motivate a separately predeclared arithmetic and
selective-QDQ strategy, but is not a complete-model fix. Native extraction and
taps may change execution. Mobile operator support, unseen-input parity and
clinical performance remain unverified. Roadmap order still prevents M5 work.

## Open questions

- Is there an actionable residual arithmetic strategy that meets the fixed contract?
- What explicit static QDQ scope and mobile runtime can satisfy the unchanged budgets?
- Do humans accept this diagnostic protocol and the continued M4 blocker?

## Confidence

High for the previously tested replay building blocks; complete-layer results
and any deployable arithmetic strategy remain unverified before execution.
