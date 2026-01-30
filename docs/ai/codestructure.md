# Code Structure

> This document describes the codebase organization for the AI agent.

## Current Directory Layout

```
Lead-Generator/
├── .claude/
│   ├── commands/           # Custom Claude Code commands
│   │   ├── onboard.md
│   │   ├── feature-new.md
│   │   ├── planner.md
│   │   ├── execute.md
│   │   ├── tests.md
│   │   ├── refactor.md
│   │   ├── pr.md
│   │   ├── pr-comments.md
│   │   ├── submit.md
│   │   └── fullworkflow.md
│   └── settings.json       # Permissions configuration
├── docs/
│   ├── ai/                 # AI context maps (this folder)
│   │   ├── architecture.md
│   │   ├── codestructure.md
│   │   ├── datamodel.md
│   │   ├── integrations.md
│   │   ├── api-endpoints.md
│   │   ├── utilities.md
│   │   └── technical-debt.md
│   └── features/           # Feature specifications
│       ├── README.md       # Feature index
│       └── _template.md    # Feature spec template
├── scripts/
│   ├── fullworkflow.bat    # Windows CMD automation
│   ├── fullworkflow.ps1    # PowerShell automation
│   └── fullworkflow.sh     # Bash automation
└── CLAUDE.md               # Project context for Claude
```

## Source Code Structure

🚧 **Not yet created** - Source code directories will be added when the first feature is implemented.

## File Naming Conventions

- Feature specs: `docs/features/<slug>.md` (kebab-case)
- Feature branches: `feature/<slug>` (kebab-case)
- Source files: TBD based on chosen framework

## Module Organization

To be defined when technology stack is chosen.
