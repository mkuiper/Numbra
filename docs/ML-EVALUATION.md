# PLACEHOLDER component evaluation

M3's evaluation library is `ml/src/numbra_ml/evaluation.py`. It evaluates
**synthetic circle / synthetic square** targets only. No baseline model has been
trained and no model performance is reported by this iteration.
[ADR-009](../decisions/ADR-009-component-evaluation.md) records the implementation
choices; [ADR-001](../decisions/ADR-001-task-framing.md) defines the count guards
and illustrative sensitivity/specificity targets.

## Input and fit isolation

Use `read_component_index(manifest_path, preparation_report_path)` to verify the
frozen manifest checksum and companion component partition. It selects one index
image per component by the first sorted record ID, before scoring. Train/score
that image rather than interpreting every view as independent. Quarantined
component IDs/reasons are retained separately. Known source-scoped group/patient
and exact byte-hash links must remain in the same component; decoded/near-visual
links are trusted from the existing preparation audit, not recomputed.

`component_predictions(index, logits)` requires exactly one finite logit per active
component ID. This mapping comes from future model inference, with the split,
target and source metadata supplied by the frozen index. A missing or non-finite
logit fails evaluation; failures must be handled explicitly by later screening
and workflow reporting, never replaced with score zero.

`evaluation_report(predictions, held_out_source=index.held_out_source)` fits only
calibration components, selects only threshold-validation components, then applies
frozen settings to test and held-out source. Its input guard rejects duplicate
component IDs across partitions and held-out-source boundary violations. The
library cannot prove the model producer trained on training components only;
the forthcoming training command/tests must establish that separately.

The default generated profile has 20 threshold components/class and must use
an **unselected refer-all** fallback. The declared `selection_exercise` profile
has 102/class and can exercise selection, subject to its 52/class independent
calibration-fit partition. Counts are guardrails, not clinical sample-size proof.

## Output contract

All nested metric blocks carry PLACEHOLDER. Reports include target names,
calibration/threshold fit hashes, counts, inclusive threshold comparison,
unavailable/selected status, degenerate selection labels, and a single held-out
source (one leave-one-source-out fold). The secondary endpoint is sensitivity at
illustrative specificity >=0.80; it does not replace the primary sensitivity
>=0.95 endpoint. Below count guards both are unavailable with threshold zero.

Sensitivity/specificity use exact two-sided 95% binomial intervals. ROC AUC uses
mean ranks for ties and is null without both classes. Empty strata return null
metrics. Calibration summaries contain Brier score, stable binary log loss,
reliability-bin counts/means and ECE. Ten equal-width bins include probability one
in the final bin. Pre/post calibration summaries are descriptive; fitted
calibration-partition results are in-sample. Selected-threshold intervals are also
descriptive after search; frozen test intervals concern an independent fixed
threshold within the generated fixture.

Source membership summaries can overlap because one linked component can contain
several development sources. Synthetic colour strata use consistent component
annotations; missing/partially missing/conflicting annotations stay explicit.
They provide no human skin-tone or fairness evidence. Neither a sigmoid nor
bounded temperature scaling makes a score clinically calibrated probability.

## Verification and remaining work

Run from the repository root:

```bash
ml/.venv/bin/python -m pytest ml/tests/test_evaluation.py -q
bash scripts/check.sh
```

Tests generate their images in ignored temporary directories. They cover
component/index/checksum integrity, quarantine, repeated-unit inflation, exact
count boundaries, fit split isolation, frozen test/holdout independence, ties,
secondary sentinel, closed-form interval endpoints/interior, ROC ties, stable
extreme logits, missing/single-class/empty metrics and source/colour breakdowns.
All logits in tests are invented arithmetic fixtures, not model predictions.

The model/training CLI, script-written `ml/reports/` artifacts, reproducible
checkpoint/dependency evidence, seeded component bootstrap uncertainty, hardware/
runtime provenance and model card remain unbuilt. No completed-M3 or clinical
performance claim is made. End-to-end referral-rule/workflow metrics belong to M6.

## Open questions

- Do humans approve ADR-009's engineering choices and the broader ADR-001 protocol?
- What representative independent real cohort could support clinical evaluation?

## Confidence

High for tested PLACEHOLDER evaluation primitives; baseline training, full report
integration and clinical validity remain unestablished.
