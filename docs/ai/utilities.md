# Utilities

> This document describes shared utilities and helper functions.

## Status

🚧 **Not yet created** - Utilities will be documented as they are implemented.

## Automation Scripts

### Workflow Scripts (scripts/)

| Script | Platform | Usage |
|--------|----------|-------|
| `fullworkflow.bat` | Windows CMD | `fullworkflow.bat <slug>` |
| `fullworkflow.ps1` | PowerShell | `.\fullworkflow.ps1 -FeatureSlug <slug>` |
| `fullworkflow.sh` | Bash | `./fullworkflow.sh <slug>` |

### Claude Commands (.claude/commands/)

| Command | Purpose |
|---------|---------|
| onboard | Initialize repo context |
| feature-new | Start new feature |
| planner | Plan implementation |
| execute | Implement feature |
| tests | Generate tests |
| refactor | Safe refactoring |
| pr | Create pull request |
| pr-comments | Handle PR feedback |
| submit | Finalize merge |
| fullworkflow | Complete workflow |

## Planned Utilities

| Utility | Purpose | Status |
|---------|---------|--------|
| Validation | Input validation helpers | Not Created |
| Formatting | Date/number formatters | Not Created |
| API Client | HTTP request wrapper | Not Created |
| Logger | Logging utility | Not Created |

## Shared Components

<!-- To be documented when UI components are created -->
