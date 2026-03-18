# Codex Local Setup

This folder contains project-scoped Codex configuration for `urban-octo-bassoon`.

It is intentionally local-only and excluded from git so this repo can keep a tailored agent lineup without affecting other repositories on the machine.

## Environment Variables

Set these before starting Codex in this repository:

- `CONTEXT7_API_KEY`: used by `docs_researcher` for Context7 docs lookup.
- `GITHUB_PERSONAL_ACCESS_TOKEN`: used by `feature_developer`, `bugfix_developer`, and `release_manager` for GitHub-aware work such as PRs and issue context.

Example shell setup:

```bash
export CONTEXT7_API_KEY="your-context7-key"
export GITHUB_PERSONAL_ACCESS_TOKEN="your-github-token"
```

## Agent Lineup

- `task_orchestrator`: default task lead for `TASKS.md`-driven work; decides which specialist agents are actually needed.
- `feature_developer`: main implementation agent for new features, branch work, pushes, and PR-aware development.
- `bugfix_developer`: narrow reproduce-fix-verify agent for regressions and behavior fixes.
- `release_manager`: branch, commit, push, PR, and release coordination.
- `browser_debugger`: browser repro, console, network, and interaction evidence.
- `ui_reviewer`: UX and workflow review for the admin/public route experience.
- `a11y_reviewer`: accessibility review for keyboard flow, semantics, focus, and labels.
- `security_reviewer`: auth, permissions, injection, secrets, and runtime-boundary review.
- `db_migration_reviewer`: Alembic, SQLModel, Postgres, and migration-safety review.
- `docs_researcher`: official docs lookup for OpenAI, FastAPI, Vue/Vuetify, and libraries.

## Prompt Patterns

These prompt patterns are documented here in this file: [README.md](/home/devadmin/projects/urban-octo-bassoon/.codex/README.md), under `Prompt Patterns` and `Recommended Workflows`.

Use the main agent by default and only call out a specialist when the task clearly benefits from it.

### Default Orchestrated Task

```text
Use task_orchestrator.
Work on the next meaningful item in TASKS.md.
Read the required project context first, choose the minimum useful specialist agents, implement the work, run the relevant verification, and update branch/PR state only if needed.
```

### Default Orchestrated Task With Git Flow

```text
Use task_orchestrator.
Work on the next meaningful item in TASKS.md.
Create a branch, choose the minimum useful specialist agents, implement the work in reviewable commits, run the relevant tests, push the branch, and open or update the PR if appropriate.
```

### Orchestrated Task With Explicit Review Gates

```text
Use task_orchestrator.
Work on the next task in TASKS.md that is ready to execute.
Use the fewest specialist agents needed, but include security_reviewer for auth/runtime/public-surface changes, db_migration_reviewer for schema changes, and ui_reviewer for user-visible workflow changes.
Implement the work, verify it, and summarize what changed plus any remaining risks.
```

### Feature Work

```text
Use feature_developer for this task.
Create a new branch, implement the feature in small reviewable commits, run the relevant tests, push the branch, and open or update the PR if needed.
Task: ...
```

### Bug Fix

```text
Use bugfix_developer for this task.
Reproduce the issue first, implement the smallest safe fix, add regression coverage if practical, run the relevant tests, and push the branch.
Task: ...
```

### PR / Release Mechanics

```text
Use release_manager.
Create or update the branch, clean up commits if needed, push the branch, open or update the PR, and summarize what shipped.
Context: ...
```

### UI Investigation

```text
Use browser_debugger first, then ui_reviewer if needed.
Reproduce the issue in the browser, capture exact repro steps plus console/network evidence, then review the UX impact.
Issue: ...
```

### Accessibility Review

```text
Use a11y_reviewer.
Review this flow for keyboard access, focus order, labeling, semantics, and screen-reader-visible regressions.
Scope: ...
```

### Security Review

```text
Use security_reviewer.
Review this change for auth, authorization, injection, secret handling, connector/runtime trust boundaries, and realistic exploit paths.
Scope: ...
```

### Migration Review

```text
Use db_migration_reviewer.
Review this Alembic or schema change for Postgres safety, backfill risk, lock-heavy DDL, downgrade realism, and model drift.
Scope: ...
```

### Docs Lookup

```text
Use docs_researcher.
Verify the official docs for this API/framework behavior and cite the authoritative source before we implement anything.
Question: ...
```

### Generic “Just Move the Repo Forward” Prompt

```text
Use task_orchestrator.
Pick up the next high-value task from TASKS.md, make reasonable decisions, use only the specialist agents that are clearly useful, and carry the work through implementation and verification.
If branch or PR work becomes relevant, bring in release_manager.
```

## Recommended Workflows

### Standard Feature Cycle

1. Ask for `feature_developer`.
2. If the UI is complex, ask for `browser_debugger` or `ui_reviewer`.
3. If the change touches auth, connectors, runtime trust boundaries, or public surfaces, ask for `security_reviewer`.
4. If the change includes Alembic or SQLModel schema changes, ask for `db_migration_reviewer`.
5. Ask for `release_manager` if you want help with PR creation, PR updates, or release notes.

### Standard Bugfix Cycle

1. Ask for `bugfix_developer`.
2. Use `browser_debugger` first if the failure is user-visible or timing-sensitive.
3. Add `ui_reviewer`, `security_reviewer`, or `db_migration_reviewer` only when the fix touches those concerns.
4. Use `release_manager` for branch/PR cleanup and shipping.

### Standard “Work On The Next Task” Cycle

1. Ask for `task_orchestrator`.
2. Let it choose `feature_developer` or `bugfix_developer` based on whether the next item is net-new work or a regression fix.
3. Add `browser_debugger`, `ui_reviewer`, `a11y_reviewer`, `security_reviewer`, `db_migration_reviewer`, or `docs_researcher` only when the task genuinely needs that expertise.
4. Use `release_manager` only when you want branch, push, PR, or release coordination.

## Notes

- Keep GitHub-aware roles narrow so GitHub MCP is only started when it is actually needed.
- Keep docs lookups on `docs_researcher` so the main agent stays lean.
- Prefer one strong implementation agent plus one targeted reviewer over spawning many agents at once.
- `task_orchestrator` should be the default entrypoint when you want Codex to decide which specialists to involve.
