---
description: Run complete feature workflow from onboarding to PR submission in sequence.
---

# Techjays /fullworkflow (Complete Feature Lifecycle)

Feature name/slug: $ARGUMENTS

## Overview
This command runs the entire feature development workflow in sequence:
1. Onboard (if not already done)
2. Feature New (create branch + spec)
3. Planner (plan implementation)
4. Execute (implement feature)
5. Tests (generate/expand tests)
6. Refactor (clean up if needed)
7. PR (create pull request)
8. PR Comments (handle feedback)
9. Submit (finalize and merge)

## Rules
- Stop and report if any step fails critically
- Each step must complete before moving to the next
- Update feature spec status at each transition
- Use gh CLI for all GitHub operations

## Workflow Execution

### Step 1: Onboard Check
1) Check if `CLAUDE.md` exists and is populated
2) Check if `docs/ai/` files exist
3) If missing: run full onboarding
4) If exists: skip to Step 2
5) **Status:** Ready for feature development

### Step 2: Feature New
1) Derive slug from $ARGUMENTS (lowercase, hyphen-separated)
2) Create branch: `git checkout -b feature/<slug>`
3) Create `docs/features/<slug>.md` from template
4) Add entry to `docs/features/README.md` (Status: Draft)
5) Commit: `chore(feature): initialize <slug> spec`
6) **Status:** Draft

### Step 3: Planner
1) Read `CLAUDE.md` + `docs/ai/*` for context
2) Open `docs/features/<slug>.md`
3) Fill/update all sections:
   - Objective, Scope, Requirements
   - Data model impact, Integration impact
   - Code impact, Test plan, Rollout plan
4) Update feature Status to `Planned`
5) **Status:** Planned

### Step 4: Execute
1) Confirm on branch `feature/<slug>`
2) Read feature spec requirements
3) Implement in small increments
4) Update feature spec if new impacts discovered
5) Run unit tests for affected modules
6) Update feature Status to `In Progress`
7) **Status:** In Progress

### Step 5: Tests
1) Read feature spec Test Plan section
2) Implement unit tests first
3) Implement integration/e2e tests if applicable
4) Run all tests and fix failures
5) Update feature spec with test file paths
6) **Status:** In Progress (tests complete)

### Step 6: Refactor (Optional)
1) Identify code that needs cleanup
2) Ensure tests provide safety net
3) Refactor in small commits
4) Run lint/tests after each change
5) Update `docs/ai/technical-debt.md` if items resolved
6) **Status:** In Progress (refactored)

### Step 7: PR
1) Run full quality gates (lint, test, build)
2) Generate PR title from feature name
3) Generate PR body from feature spec
4) Push branch: `git push -u origin feature/<slug>`
5) Create PR: `gh pr create --title "..." --body "..."`
6) Update feature Status to `In Review`
7) **Status:** In Review

### Step 8: PR Comments
1) Check for PR comments: `gh pr view <PR> --comments`
2) If comments exist:
   - Address each comment
   - Run targeted tests
   - Respond via `gh pr comment`
3) If no comments: proceed to Step 9
4) **Status:** In Review (comments addressed)

### Step 9: Submit
1) Check CI status: `gh pr checks <PR>`
2) If failing: fix and re-run
3) Verify feature spec is complete
4) Update feature Status to `Done`
5) Output merge-ready summary
6) **Status:** Done

## Output
After completion, report:
- Feature slug and branch name
- PR URL
- All files created/modified
- Test results summary
- Any items requiring manual attention
