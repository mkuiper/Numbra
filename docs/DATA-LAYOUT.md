# Local data layout

The entire `data/` directory is git-ignored, including its README. Do not force-add
files from it. This tracked document replaces an in-data README so the stronger
autopilot rule (no committed data) is unambiguous.

Planned layout for M2:

```
data/
  README.md             # optional local reminder; never committed
  raw/<source>/<version>/
  prepared/<run-id>/
  manifests/<run-id>.jsonl
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

- ADR-006 defines JSONL schema 1.1.0; M2 must document its duplicate audit and
  component split metadata.
- How should M4 regenerate and package its model reproducibly during Android builds?

## Confidence

High on repository boundaries; medium on the proposed layout before M2 implementation.
