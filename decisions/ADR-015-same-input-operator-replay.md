# ADR-015 — Training-only PLACEHOLDER same-input operator replay

Date: 2026-10-09

Status: Accepted (autopilot) — pending human review

## Context

ADR-014's corrected taps retain separate BatchNormalization nodes but fail the
unchanged ADR-011 budgets. Accumulated boundary drift cannot identify local
kernel arithmetic. The selected saved model, training split and failed artifacts
remain the reference; ADR-012's toy diagnostic workaround remains in force.

## Decision — declared before execution

Replay the first Conv and the first depthwise Conv (groups = input channels =
output channels, greater than one), and their immediately following saved BN
nodes. Select by module order and graph connectivity, never by measured errors.
Use all and only existing training component index images. Verify saved model,
preparation, retained experiments and the corrected preserved graph/report
hashes before inference; refuse absent/ambiguous matches and stale provenance.

Tap inputs and pre-activation outputs in a separate preserved-graph copy.
Capture Python module inputs, ordinary Conv outputs and timm BN drop inputs,
copying before in-place activation. Compare tapped vs original logits and remove
every hook even on failure. Extract each original operator with its exact saved
parameters and attributes; serialize/audit its disabled-optimisation ORT graph.
Use the existing CPU/sequential/two intra-op/one inter-op profile throughout.

For each operator, replay both the exact Python input and the exact tapped ORT
input through Python and ORT. Separate same-input kernel differences, propagated
input differences and replay-vs-whole-graph differences. Check their signed
elementwise telescoping identity in float64; aggregate maxima cannot be added
as an exact worst-case decomposition. Report Python replay fidelity as well.
Standalone extraction can change execution and does not prove a deployed graph
will behave identically.

For each BN on both input origins, additionally measure three predeclared
float32 primitive graphs: subtract/divide/multiply/add; affine coefficients
computed as weight * rsqrt(variance + epsilon); and affine coefficients computed
as weight / sqrt(variance + epsilon). Coefficients use saved float32 buffers.
Compare each primitive graph to its Python implementation and native Python BN.
Also report a float64 formula rounded once to float32 as a diagnostic arithmetic
reference, not a replacement for the saved float32 model. This does not fit
anything, change weights, select a deployment graph or promise a fix.

Keep graph copies, ordered component diagnostics and tensor outputs in ignored
data/. Track only aggregates, provenance and checksums. Every artifact/report
is **PLACEHOLDER diagnostic, never bundle**. No test/held-out/stress inference,
quantisation fitting, retraining, fit/interface/budget change or M4 closure.
Declare the next complete arithmetic/precision/quantised-scope strategy using
training evidence before any frozen evaluation.

## Consequences

M4 stays incomplete. This narrows a numerical engineering investigation while
retaining every existing failure. It establishes neither Android compatibility
nor unseen-input parity nor clinical performance. Tests will cover depthwise
selection, pre-activation semantics, cleanup, extraction, replay fidelity,
training-only isolation and provenance rejection using generated fixtures.

## Observed follow-through — 2026-10-09 UTC

[Aggregate evidence](../ml/reports/PLACEHOLDER-m4-replay1.json): 152 existing
training inputs, unchanged state hashes, no frozen evaluation or fit/selection.
All four operators have zero Python/ONNX replay-fidelity error; tap/original
logits and signed telescoping residuals are zero. Stem Conv local maximum is
0.000000476837. Stem BN local maximum is 0.000000953674, versus propagated
maximum 0.00000667572. First depthwise Conv local maximum is 0.000000119209;
its BN local maximum is 0.00000762939 versus propagated 0.0000457764.
Separate maxima cannot be added as a worst-case decomposition.

Every primitive ONNX BN graph matches its Python formula exactly on both input
origins. None eliminates native-Python BN differences: maxima are 0.000000953674
and 0.00000762939 at the two layers. The rounded float64 formula also differs
from native Python. These are operator measurements, not a passing complete
model or evidence that greater precision solves the saved-reference contract.
The next experiment should declare promoted Conv accumulation and fused-affine
BN emulation; original float32 weights/stage boundaries/reference remain fixed.
Full graph and quantised scope must be declared before frozen evaluation.
See [export documentation](../docs/ML-EXPORT.md) for interpretation and limits.

## Open questions

- Can an explicitly declared arithmetic strategy meet the original budgets?
- Which quantised scope can preserve the selected baseline's referral decisions?
- Do humans accept this additional diagnostic protocol?

## Confidence

High for observed same-input arithmetic, tested isolation and replay fidelity
on the training fixtures. A successful deployment precision/quantised strategy,
unseen-input parity, Android support and clinical performance remain unverified.
