# PatchMap

Evidence-bound provenance graph for AI-assisted code changes: requirement -> changed hunk -> passing test -> exact commit.

`PROVEN` requires explicit passing evidence bound to a known requirement, known changed hunk, and exact commit. Agent narration, unrelated green tests, failed tests, wrong commits, and unknown hunks do not count.

## Quick start
```bash
python -m pip install -e .
patchmap --spec requirements.txt --diff change.diff --evidence evidence.json --commit <sha> --out patchmap-out
```
Outputs: deterministic `graph.json` and `report.md`. PatchMap refuses to overwrite a non-empty output directory.
