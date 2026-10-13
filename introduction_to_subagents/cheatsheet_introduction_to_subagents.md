# Introduction to Subagents: Cheat Sheet

4 lessons, ~45 min. Delegate work to isolated Claude subagents and keep your main context clean.

> Built from the course outline plus general Claude Code knowledge. Check frontmatter fields and `/agents` options against your installed version.

---

## 1. How Subagents Work

```
Main session (your context)
   |  task description (the ONLY input the subagent gets)
   v
Subagent: fresh, separate context window + own system prompt + limited tools
   |  does the work (reads files, runs commands...)
   v
Final summary only  -->  back to main session
```

- Each subagent starts with a **clean context**: it does not see your conversation history.
- Everything it needs must be in the **task prompt** Claude sends it (file paths, goal, constraints).
- All the noise (files read, searches, failed attempts) stays in the subagent's window. Main context gets just the **result**.
- Multiple subagents can run **in parallel**.
- Subagents generally can't spawn further subagents.

### Why bother
| Benefit | How |
|---|---|
| Context stays clean | Heavy exploration happens elsewhere |
| Speed | Parallel work on independent tasks |
| Focus | Specialized prompt + restricted tools per job |
| Safety | Read-only reviewers can't edit by accident |

---

## 2. Create a Subagent

### With `/agents`
`/agents` -> **Create new agent** -> choose scope -> describe it (or let Claude draft it) -> pick tools -> pick model -> save.

### What it is: a Markdown file with frontmatter
| Scope | Location | Use |
|---|---|---|
| Project | `.claude/agents/<name>.md` | Shared with team via git |
| User | `~/.claude/agents/<name>.md` | Personal, all projects |

```markdown
---
name: code-reviewer
description: Reviews code for bugs, security issues and style. Use proactively after code changes.
tools: Read, Grep, Glob
model: haiku
---

You are a senior code reviewer. Review the changed files.

Output format:
## Summary (1-2 lines)
## Issues (severity: high/med/low, file:line, fix)
## Blockers (anything you could not check, and why)

Rules: do not edit files. Report only what you verified.
```

| Field | Notes |
|---|---|
| `name` | Lowercase, hyphens |
| `description` | **What Claude reads to decide when to delegate**; say what it does and when to use it |
| `tools` | Allowlist; omit to inherit all (avoid this) |
| `model` | `haiku` / `sonnet` / `opus` / inherit. Cheap model for simple jobs |

### Invoking
- **Automatic**: Claude delegates when the task matches the `description`.
- **Explicit**: "Use the code-reviewer subagent on the auth changes."
- Phrases like "use proactively" in the description encourage auto-delegation.

---

## 3. Design Reliable Subagents

### Structured output format
The main agent only sees the final message, so define exactly what it contains.
- Fixed sections (Summary / Findings / Blockers), severity levels, `file:line` references.
- Predictable format means the main agent can act on it without re-reading files.
- Ask for **brevity**: summaries, not transcripts.

### Obstacle reporting
- Tell the subagent to report what blocked it: missing access, failed commands, files not found, assumptions made.
- Without this, a subagent may quietly give a confident answer built on a failed step.
- Example rule: "If you could not verify something, say so under Blockers. Never guess."

### Limited tool access (least privilege)
| Job | Tools |
|---|---|
| Code review, research, audit | `Read, Grep, Glob` (read-only) |
| Test runner | `Read, Bash` |
| Doc generator | `Read, Grep, Glob, Write` |
| Fixer | add `Edit` |

Fewer tools = fewer mistakes and a smaller blast radius.

### Prompt tips
- One job per subagent; a narrow role beats a generalist.
- Put the process, output format, and "do not" rules in the system prompt.
- Make descriptions distinct so Claude picks the right agent.

---

## 4. Example Workflows
- **Code review**: read-only reviewer returns issues by severity.
- **Documentation generation**: reads modules, writes docs, returns the list of files created.
- **Codebase research**: "where is auth handled?" is explored in isolation; only the answer returns.
- **Parallel audit**: security, performance, and test-coverage reviewers run at once; the main agent merges their reports.

---

## 5. When to Use Subagents (and When Not)

### Good fit
- Output is large but you only need a **summary** (searching, log analysis, reviews).
- Tasks are **independent**, so they can run in parallel.
- A task needs a **different tool set or role** than the main session.
- You want the main context kept free for the real work.

### Anti-patterns
| Mistake | Why it hurts |
|---|---|
| Tiny tasks (rename a variable) | Startup overhead exceeds the benefit |
| Tightly **sequential/dependent** steps | Context must be passed by hand each hop |
| Work needing **back-and-forth** with you | Subagents can't ask you mid-run |
| Vague task prompt | Subagent has no history; it guesses |
| Giving every agent all tools | Defeats isolation and safety |
| Many overlapping agents | Claude picks wrong ones; descriptions blur |
| Trusting the summary blindly | It's a report, not proof: verify high-stakes claims |
| Expecting the main agent to see what the subagent saw | It only gets the final message |

Rule of thumb: delegate **self-contained, summarizable** work; keep **interactive, context-heavy** work in the main session.

---

## 6. Quick Reference

| Need | Do |
|---|---|
| Create one | `/agents` or add `.claude/agents/<name>.md` |
| Share with team | Project scope + commit to git |
| Make it auto-trigger | Specific `description`, "use proactively" |
| Call it directly | "Use the `<name>` subagent to..." |
| Make it safe | Restrict `tools` to the minimum |
| Make it cheap | `model: haiku` |
| Make output usable | Define sections + a Blockers section |

## 7. Pitfalls
- Assuming the subagent knows what you discussed earlier.
- Omitting `tools` so it inherits everything.
- No output format, so you get a long, unusable narrative.
- No obstacle reporting, so failures are hidden.
- Using subagents for quick one-step jobs.
