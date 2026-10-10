# Claude Code in Action: Cheat Sheet

Goal: run Claude Code past the quick task: long, less supervised, team-wide, and still trustworthy.

> Built from the course outline plus general Claude Code knowledge. Verify flag names and slash commands against `/help` and the docs for your installed version.

---

## 1. Steer the Work

| Need | Tool | Notes |
|---|---|---|
| Scope before touching code | **Plan mode** (`Shift+Tab` to cycle modes) | Claude reads and proposes a plan; no edits until you approve |
| Context getting long | `/compact <instructions>` | Tell it what to keep: `/compact keep the API schema decisions and failing test names` |
| Fresh start, same repo | `/clear` | Drops conversation, keeps CLAUDE.md |
| Undo a bad turn | **Rewind** (`Esc Esc` or `/rewind`) | Restore conversation and/or code to an earlier point |
| Resume earlier work | `claude -c` (continue) / `claude -r` (resume picker) | |

### Hands-on vs autonomous
- **Hands-on steering**: unclear scope, risky area, exploring. Small prompts, review each step.
- **Autonomous goal / loop runs**: clear success criteria, checkable by tests. Give a goal, let it iterate, verify at the end.
- Rule of thumb: the less you watch, the more you must verify afterwards (see section 4).

### Good steering habits
- Plan first for anything touching more than ~3 files.
- Compact **with instructions** at natural boundaries (feature done, before switching subtasks), not when context is already degraded.
- Rewind instead of arguing: a bad turn left in context keeps influencing later ones.
- State the finish line: "done when `pytest tests/auth` passes and no new lint errors."

---

## 2. Configure Claude

### CLAUDE.md (lean, followed)
- Loaded every session, so every line costs context. Keep it short.
- Include: build/test/lint commands, repo layout gotchas, conventions Claude can't infer, hard "never do X" rules.
- Exclude: things obvious from the code, long prose, anything that must be *enforced* (use hooks).
- Locations: `~/.claude/CLAUDE.md` (personal), `./CLAUDE.md` (team, committed), subdirectory CLAUDE.md (scoped).
- `/init` bootstraps one; then prune it.
- `#` shortcut or editing directly adds memory notes.

```markdown
# Project
## Commands
- Test: `pytest -q`   Lint: `ruff check .`
## Rules
- Never edit `migrations/` by hand; generate with `alembic revision`.
- Use `haiku` model IDs only in dev code.
```

### Skills (repeatable procedures)
- Folder with `SKILL.md` (frontmatter `name`, `description` + instructions) under `.claude/skills/<name>/` (project) or `~/.claude/skills/` (personal).
- Description decides when Claude loads it, so write it as a trigger ("Use when preparing a release...").
- Package: release checklist, PR template, migration procedure, data-fix runbook.
- Rule: if you paste the same instructions three times, make it a skill.

### Permission modes

| Mode | Behavior | Use for |
|---|---|---|
| default | Asks before edits/commands | Unfamiliar code |
| acceptEdits | Auto-approves file edits | Trusted refactors |
| plan | Read-only planning | Scoping |
| bypassPermissions | No prompts | Only in sandbox/container, never on a real machine with secrets |

- Pre-approve safe commands via allowlist in `.claude/settings.json` (`permissions.allow`), deny dangerous ones (`permissions.deny`).

### Hooks (enforce what can't be skipped)
CLAUDE.md is advice; **hooks are guarantees**. They are shell commands run by the harness on events.

| Event | Typical use |
|---|---|
| `PreToolUse` | Block dangerous commands, protect files |
| `PostToolUse` | Auto-format, lint after edits |
| `UserPromptSubmit` | Inject context, validate prompts |
| `Stop` | Gate "done" on passing tests |

- Configured in `settings.json`. A hook exiting with **code 2** blocks the action and feeds stderr back to Claude.

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "./scripts/block-protected.sh" }] }
    ]
  }
}
```

---

## 3. Automate Repeat Work

| Mechanism | What it is | When |
|---|---|---|
| **Routines** (`/schedule`) | Prompts scheduled to run on Anthropic infrastructure | Nightly triage, weekly dep check, recurring reports |
| **`/loop`** | Re-run a prompt/command on an interval in-session | Polling CI, babysitting a deploy |
| **Headless** (`claude -p "prompt"`) | Non-interactive, scriptable | Your own pipeline, cron, CI steps |
| **Managed code review** | Claude reviews PRs automatically | Every PR, first-pass review |
| **GitHub Action** (`anthropics/claude-code-action`) | Claude in your Actions workflows; `@claude` mentions | Issue to PR, PR comments, custom workflows |

### Headless essentials
```bash
claude -p "Summarize failing tests" --output-format json   # structured output
claude -p "Fix lint errors" --allowedTools "Edit,Bash(ruff:*)"
cat build.log | claude -p "Explain the failure"            # piping works
```
- Use `--output-format json` or `stream-json` to parse results in scripts.
- Always scope `--allowedTools`; there is no human to approve prompts.
- Choose **routines** if Anthropic-hosted scheduling is enough, **headless** if you need your own infra/pipeline control.

### GitHub setup
- `/install-github-app` in Claude Code wires up the app and secrets.
- Workflow triggers: `pull_request`, `issue_comment` (for `@claude`), `issues`.
- Store `ANTHROPIC_API_KEY` as a repo secret; never commit it.

---

## 4. Verify and Share

### Verify in proportion to how little you watched
| You watched... | Verify with... |
|---|---|
| Every step | Skim diff |
| Some steps | Run tests + read diff of risky files |
| Nothing (autonomous/scheduled) | Independent test run, full diff review, check for deleted/skipped tests, spot-check behavior |

Red flags in unsupervised output: tests deleted or weakened, `skip`/`xfail` added, broad try/except, mocked-away logic, changes outside the stated scope.

### Gate on real results
- `Stop` hook runs the test suite; non-zero exit sends Claude back to fix instead of finishing.
- Prefer **real test output** over Claude's claim "tests pass."
- Ask Claude to show the command it ran and its raw output.

### Plugins (share a trusted setup)
- Bundle skills, slash commands, subagents, hooks, MCP servers into one installable unit.
- Team installs the same setup, so the same rules and workflows everywhere.
- Package only what you've proven out in your own sessions.

---

## 5. Quick Reference

| Task | Command |
|---|---|
| Cycle permission/plan modes | `Shift+Tab` |
| Compact with focus | `/compact <what to keep>` |
| Rewind | `Esc Esc` / `/rewind` |
| Clear | `/clear` |
| Init CLAUDE.md | `/init` |
| See / edit hooks | `/hooks` |
| Manage permissions | `/permissions` |
| MCP servers | `/mcp` |
| Context usage | `/context` |
| Headless | `claude -p "..."` |
| Pick model | `/model` |

## 6. Decision Flow

```
New task
 ├─ Unclear / multi-file?  -> Plan mode first
 ├─ Clear + testable?      -> Autonomous run, then verify
 ├─ Rule must never break? -> Hook, not CLAUDE.md
 ├─ Repeated procedure?    -> Skill
 ├─ Repeats on a schedule? -> Routine (or headless + cron)
 ├─ Needs PR integration?  -> Code review / GitHub Action
 └─ Setup proven + team?   -> Plugin
```

## 7. Common Pitfalls
- Bloated CLAUDE.md that Claude partially ignores.
- Relying on CLAUDE.md for rules that need enforcement.
- `bypassPermissions` outside a sandbox.
- Compacting without instructions, so key decisions get lost.
- Trusting "all tests pass" from an unsupervised run without re-running.
- Headless jobs with unrestricted tools.
