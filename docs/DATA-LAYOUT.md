# Local data layout

The entire `data/` directory is git-ignored, including its README. Do not force-add
files from it. This tracked document replaces an in-data README so the stronger
autopilot rule (no committed data) is unambiguous.

Implemented M2 layout (generated content remains local):

```
data/
  README.md             # optional local reminder; never committed
  prepared/<run-id>/
    images/*.png          # generated RGB textures only
    unassigned.jsonl      # raw generator provenance, before split assignment
    manifest.jsonl        # frozen schema 1.1.0 prepared rows
    preparation-report.json # component/duplicate/quarantine/split audit
```

All images, source metadata, patient identifiers, manifests, and derivative data
stay local. Source permissions and approval come from the dataset ADR. Generated
synthetic fixtures are constructed by tests; no real images are test fixtures.
Models are ignored as well. M4 must document an explicit, reviewed strategy for
providing its small PLACEHOLDER artifact to the app without committing patient data.

Research publication PDFs can contain clinical figures even when they are not
task datasets. Inspect only for research evidence and delete local copies once
no longer needed; never use their figures as training data. Review-2 cleanup
removed `.firecrawl/ila-diagnosis.pdf` and `.firecrawl/ai4-supplement.pdf`; retained
text extracts are ignored evidence notes, not datasets.

## Open questions

- ADR-007 and [data preparation](DATA-PREPARATION.md) now document schema 1.1.0,
  duplicate audits and component split metadata. Future real-data layout needs
  a new dataset decision; no real raw source is acquired.
- How should M4 regenerate and package its model reproducibly during Android builds?

## Confidence

High on repository boundaries; high for generated M2 layout; future real-data layout remains unapproved.
