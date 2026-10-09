# ADR-020 — Complete PLACEHOLDER BatchNorm coefficient-rounding replay

Date: 2026-10-10

Status: Accepted (autopilot) — pending human review

## Context

ADR-019 finds local native arithmetic differences at every saved BN and most
Conv layers. Both promoted BN expressions reproduce their specified Python
formula but fail to reproduce native BN. Every baseline export remains rejected;
ADR-012's labelled toy diagnostic workaround remains in force.

## Decision — declared before execution

Replay all saved BNs in module order, matched one-to-one against the preserved
ONNX graph using ADR-019's exact parameter/geometry validation. Use all and only
152 ordered training component index images on both exact native Python inputs
and preserved-ORT inputs. Copy pre-activation boundaries before in-place timm
activations. Check native replay and tapped/original logits; retain original
saved weights, fitted scaling/head, temperature, threshold and ADR-011 budgets.

Predeclare the complete Cartesian product of these five binary rounding choices
(32 recipes, no favourable subset or adaptive recipe additions):

1. Epsilon sum: `e32` = float32(var + float32(eps)); `e64` =
   float64(var) + float64(saved Python eps).
2. Reciprocal: `r32` = float32(1 / float32(sqrt(float32(sum))));
   `r64` = 1 / sqrt(float64(sum)), retaining float64.
3. Alpha: `a32` = float32(weight * float32(reciprocal));
   `a64` = float32(float64(weight) * float64(reciprocal)).
4. Beta: `b32` = float32(bias - float32(mean * alpha));
   `b64` = float32(float64(bias) - float64(mean) * float64(alpha)).
5. Output: `o32` = float32(float32(x * alpha) + beta);
   `o64` = float32(float64(x) * float64(alpha) + float64(beta)).

All saved tensors retain their original float32 bits. The recipes may collapse
to identical arithmetic for some choices; report them all. `o64` is a rounded
float64 diagnostic, not a claim to implement a hardware float32 FMA. Implement
expressions independently in NumPy and eager PyTorch; record coefficient bits,
epsilon bits, expression disagreement and both native-relative errors rather
than presuming the engines' square roots are identical. This is a hypothesis
experiment, not an assertion about the native kernel's implementation.

Audit complete recipe/origin/layer/component scope, reconstruct aggregates from
ignored ordered details, recheck coefficient and saved-state bits, graph hashes,
source/dependency provenance, and exact prior preserved-control logits. No new
quantisation fit, frozen test/held-out/stress inference, full-model replacement,
reference/budget change or deployment selection. Tapped graphs and all results
are **PLACEHOLDER diagnostic only, never bundle**. Exit 0 means diagnostic evidence
was written; M4 remains incomplete regardless of any locally matching recipe.

## Consequences

This bounded experiment addresses coefficient rounding only. It does not fix
Conv kernel drift, establish whole-model parity, select quantisation scope, or
prove mobile operator support/performance. A separately predeclared candidate
and unchanged full acceptance checks are necessary before bundling.

## Open questions

- Does any declared recipe reproduce native BN across every tested layer/input?
- Can local arithmetic findings motivate a finite deployable conversion strategy?
- Do humans accept continued diagnostic work while M4 remains blocked?

## Confidence

High for the explicit finite protocol; outcomes, mobile and clinical validity
remain unverified before execution.
