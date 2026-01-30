# Lead-Generator

## Project Overview
Lead generation application - new project under development.

## Tech Stack
- **Status:** Not yet determined
- **Framework:** TBD
- **Language:** TBD
- **Database:** TBD

## Commands
```bash
# Install dependencies
# TBD - No package manager configured yet

# Run development server
# TBD

# Run tests
# TBD - No test framework configured yet

# Build for production
# TBD

# Lint code
# TBD
```

## Project Structure
```
Lead-Generator/
├── .claude/
│   ├── commands/       # AI workflow commands
│   └── settings.json   # Permissions config
├── docs/
│   ├── ai/            # AI context maps
│   └── features/      # Feature specifications
├── scripts/           # Automation scripts
└── CLAUDE.md          # This file
```

## Feature-first workflow (mandatory)

1. **Documentation First:** Every change must be tied to a Feature Spec located at `docs/features/<feature-slug>.md`.

2. **Planning:** The Planning phase must involve creating or updating the Feature Spec (defining objective, scope, impacted files, data model, test plan, and rollout).

3. **Execution:** Code generation and test creation must explicitly reference requirements defined in the Feature Spec.

4. **Branching Strategy:** Use the naming convention `feature/<short_meaningful_name>`.

5. **Git Operations:** Use the `gh` CLI for all GitHub operations (PR creation, comments, status checks).

## Workflow Commands

| Command | Description |
|---------|-------------|
| `/onboard` | Initialize repo and create AI context docs |
| `/feature-new <slug>` | Create new feature branch and spec |
| `/planner <slug>` | Plan implementation (no code edits) |
| `/execute <slug>` | Implement feature per spec |
| `/tests <slug>` | Generate tests from spec |
| `/refactor <slug>` | Safe refactoring with tests |
| `/pr <slug>` | Create pull request |
| `/pr-comments <slug>` | Handle PR feedback |
| `/submit <slug>` | Finalize and merge |
| `/fullworkflow <slug>` | Run complete workflow |

## GitHub Workflow Conventions

- **Branch naming:** `feature/<slug>`
- **PR creation:** `gh pr create --title "..." --body "..."`
- **PR checks:** `gh pr checks <PR>`
- **PR comments:** `gh pr comment <PR> --body "..."`

## Repository Info

- **GitHub:** https://github.com/mathankj/Lead-Generator
- **Owner:** mathankj
