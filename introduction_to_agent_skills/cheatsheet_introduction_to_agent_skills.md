# Introduction to Agent Skills: Cheat Sheet

6 lessons, ~1 hr. Reusable markdown instructions that Claude Code applies automatically to matching tasks.

> Built from the course outline plus general Claude Code knowledge. Check field limits, priority order and the validator name against the current docs and your installed version.

---

## 1. What Skills Are

- A **skill** = a folder with a `SKILL.md` (instructions + frontmatter), optionally with reference files and scripts.
- Teach Claude once instead of pasting the same guidance into every prompt.
- **Model-invoked**: Claude decides to use a skill when your request matches its `description`. No slash command needed.

### Where they live
| Scope | Location | Who gets it |
|---|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` | You, all projects |
| Project | `.claude/skills/<name>/SKILL.md` | Anyone who clones the repo |
| Plugin | bundled in a plugin | Anyone who installs it |
| Enterprise | managed settings | Whole org, centrally controlled |

### How matching works (loading)
```
Startup:     only each skill's name + description are loaded (cheap)
Request:     Claude compares your request to descriptions
Match:       full SKILL.md body is loaded into context
As needed:   linked reference files read, scripts executed
```
So installing many skills costs little until one triggers.

---

## 2. Create a Skill

```
.claude/skills/pr-review/
  SKILL.md
```
```markdown
---
name: pr-review
description: Reviews pull requests for bugs, security and style against our team checklist. Use when the user asks to review a PR, diff, or code change.
allowed-tools: Read, Grep, Glob
---

# PR Review

1. Read the changed files.
2. Check each item in the checklist below.
3. Report findings as: severity, file:line, fix.

## Checklist
- No secrets in code
- Tests added for new logic
- Errors handled, not swallowed
```

| Field | Rules |
|---|---|
| `name` | Lowercase letters, numbers, hyphens; should match the folder |
| `description` | What it does **and when to use it**; the trigger Claude matches on |
| `allowed-tools` | Optional allowlist of tools Claude may use while the skill is active |

### Verify it loads
- Restart the session after adding a skill (or confirm it is picked up), then ask: "What skills are available?"
- Make a request that should trigger it and see if Claude applies it.
- Frontmatter errors (bad YAML, missing fields, wrong indentation) mean the skill silently won't load.

---

## 3. Write Good Descriptions

The description is the **only thing Claude sees** when deciding whether to use the skill.

| Weak | Strong |
|---|---|
| "Helps with documents" | "Extracts text and tables from PDF files, fills forms, merges PDFs. Use when working with PDFs or when the user mentions forms or document extraction." |

Tips:
- Say **what** it does and **when** to use it.
- Include the words users actually say (file types, task names, keywords).
- Be specific enough not to fire on unrelated requests, and broad enough not to be missed.
- Write in third person ("Reviews...", "Generates...").

### Restrict tools with `allowed-tools`
- Read-only skills (review, audit, research): `Read, Grep, Glob`.
- Prevents edits while the skill is active; least privilege for safer behavior.

---

## 4. Organize Larger Skills (Progressive Disclosure)

Keep `SKILL.md` short; point to detail that loads only when needed.

```
.claude/skills/api-docs/
  SKILL.md              <- overview + when to read what (keep concise)
  reference/
    endpoints.md        <- loaded only if needed
    style-guide.md
  scripts/
    validate.py         <- executed, not read
```
```markdown
For endpoint details see [reference/endpoints.md](reference/endpoints.md).
To validate output run: `python scripts/validate.py <file>`
```

| Piece | Use | Context cost |
|---|---|---|
| `SKILL.md` body | Core workflow | Loaded on trigger |
| Reference files | Long specs, examples, schemas | Only when Claude reads them |
| Scripts | Deterministic work (validate, convert, parse) | Only the **output** enters context, not the code |

Rules of thumb:
- Keep `SKILL.md` well under a few hundred lines.
- Link one level deep from `SKILL.md`; avoid chains of references.
- Use scripts for anything that must be exact; Claude's judgment for the rest.

---

## 5. Skills vs Other Tools

| Tool | Loaded | Best for |
|---|---|---|
| **CLAUDE.md** | Every session, always | Short project-wide facts and rules |
| **Skills** | On demand, when matched | Task-specific procedures and standards |
| **Subagents** | When delegated, in an isolated context | Heavy, self-contained tasks; keep main context clean |
| **Hooks** | On events, by the harness | Rules that must be **enforced**, not suggested |
| **MCP servers** | When tools are called | Connecting external services and data |

Decision shortcuts:
- Applies to everything, short? -> CLAUDE.md.
- Only for certain tasks, longer? -> Skill.
- Must never be skipped? -> Hook.
- Needs external system access? -> MCP.
- Big job that would flood context? -> Subagent (can also use skills).

---

## 6. Share Skills

| Method | How | Good for |
|---|---|---|
| **Project repo** | Commit `.claude/skills/` to git | A team on one codebase |
| **Plugin** | Bundle skills (plus commands, hooks, agents) and distribute | Cross-repo sharing, versioned installs |
| **Enterprise managed settings** | Admin-deployed | Org-wide standards, mandatory skills |
| **Custom subagents** | Reference skills from a subagent's config | Specialized agents with built-in expertise |

Note: subagents don't automatically inherit your skills; give them the ones they need explicitly.

---

## 7. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Skill never triggers | Vague description, missing keywords | Rewrite description with what + when + user phrasing |
| Skill not listed | Wrong path, bad YAML, name mismatch | Check folder location, frontmatter, filename `SKILL.md` |
| Triggers on wrong tasks | Description too broad | Narrow it, add exclusions |
| Wrong skill wins | Priority conflict: same name in multiple scopes | Rename, or remove the duplicate; higher-priority scope overrides |
| Script fails at runtime | Missing permission, dependency, wrong path | Run it manually; check the executable bit and relative paths |
| Behavior differs from expectation | Skill loaded but instructions ambiguous | Tighten steps; add an example |

Tools:
- **Skills validator**: checks frontmatter and structure before you ship.
- **`claude --debug`**: shows skill discovery and loading, and surfaces errors.

---

## 8. Quick Reference

| Task | Do |
|---|---|
| New personal skill | `~/.claude/skills/<name>/SKILL.md` |
| New team skill | `.claude/skills/<name>/SKILL.md`, commit it |
| Make it trigger | Specific `description` with what + when + keywords |
| Make it read-only | `allowed-tools: Read, Grep, Glob` |
| Keep it lean | Reference files + scripts, linked from `SKILL.md` |
| Debug | `claude --debug` + validator |

## 9. Pitfalls
- Description that says what but not when.
- A giant `SKILL.md` that defeats progressive disclosure.
- Putting must-enforce rules in a skill instead of a hook.
- Duplicate skill names across scopes causing silent overrides.
- Assuming subagents have your skills.
- Broken YAML frontmatter: the skill fails quietly.
