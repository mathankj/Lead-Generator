---
description: Start a feature: create branch feature/<slug> and create docs/features/<slug>.md from template.
---

# Techjays /feature-new

Feature name/slug: $ARGUMENTS

## Rules
- Must create branch: `feature/<short_meaningful_name>`
- Must create feature spec: `docs/features/<slug>.md`
- Use git + gh CLI where appropriate.

## Steps
1) Derive a slug:
   - lowercase
   - hyphen-separated
   - no dates
2) Create branch:
   - `git checkout -b feature/<slug>`
3) Create `docs/features/<slug>.md` using the standard template.
4) Add entry to `docs/features/README.md` (Status: Draft).
5) Commit:
   - message: `chore(feature): initialize <slug> spec`
6) Output:
   - feature slug
   - branch name
   - path to feature spec
