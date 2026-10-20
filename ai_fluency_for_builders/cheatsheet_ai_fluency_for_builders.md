# AI Fluency for Builders: Cheat Sheet

9 lessons, ~3 hr. The 4D Framework (Delegation, Description, Discernment, Diligence) applied to product people, engineers and makers who own the full arc from problem to shipped solution. Built with CodePath. Builds on *AI Fluency: Framework and Foundations*.

> Built from the course outline plus general knowledge. The outline names the Description Chain and the five lenses but not every step, so I've marked inferred details. Check them against the lessons.

---

## 1. The 4Ds for Builders

| D | Builder question |
|---|---|
| **Delegation** | What does AI do, what stays my judgment, at each stage of building? |
| **Description** | Can I turn a messy user need into an instruction AI can act on precisely? |
| **Discernment** | Is what AI produced actually good, beyond "it works"? |
| **Diligence** | Do I stand behind what ships, and should it exist at all? |

Core idea: AI speeds up implementation, so **human judgment becomes the differentiator**: deciding what to build, defining done, evaluating, and owning the result.

### Inner loop vs outer loop
| Loop | What it is | Examples |
|---|---|---|
| **Inner loop** | Fast cycle of writing, running, fixing | Code, tests, debugging, iterating with AI |
| **Outer loop** | Slower cycle around it: whether to build, for whom, and did it work | Customer problem, requirements, release, post-launch feedback |

AI is strong in the inner loop. Most of your value (and risk) sits in the outer loop.

### Reusable brief
A short document you hand to AI up front with your **values, constraints, and context** (stack, conventions, quality bar, what to avoid, who the users are) so you don't re-explain each time. Same idea as a CLAUDE.md or system prompt.

Try it: map your current work to the 4Ds and find where you're weakest (often Discernment or Diligence).

---

## 2. How AI Works (and Fails)

- LLMs are trained on large text/code corpora to predict the next token, then tuned to follow instructions and be helpful and safe.
- Good at: boilerplate, refactors, tests, translating between formats, explaining code, first drafts of designs.
- Predictable failures:

| Failure | Builder consequence |
|---|---|
| Plausible but wrong output (hallucinated APIs, packages, facts) | Code that looks right and doesn't run or is subtly wrong |
| Limited context | Misses conventions or dependencies elsewhere in the codebase |
| Confident tone regardless of correctness | Easy to over-trust |
| Weak on novel, ambiguous or underspecified problems | Needs your problem framing |
| Optimizes for "works" over maintainability, security, taste | Quality debt accumulates |

Set expectations for each task from this list, not from the model's confidence.

---

## 3. Delegation: Decompose the Problem

Walk the **builder's toolkit** across the stages of a customer problem and decide AI's role at each:

```
Understand the problem -> Define done -> Design -> Implement -> Test -> Review -> Ship -> Learn
```
| Stage | AI can | You keep |
|---|---|---|
| Understand | Summarize research, draft questions | Which problem matters; talking to users |
| Define done | Draft test cases | The criteria and priorities |
| Design | Generate options | Choice, trade-offs, taste |
| Implement | Write most of the code | Architecture, constraints |
| Test | Generate tests, find edge cases | Whether tests actually capture intent |
| Review | First-pass review | Final judgment |
| Ship / Learn | Draft release notes, analyze feedback | The ship decision, and what to do about it |

Rule: delegate in proportion to your ability to **verify**.

### Acceptance tests: define done first
Write them **before any code exists**.
- Describe observable behavior from the user's side, including edge cases and failure modes.
- Format: Given / When / Then, or plain input -> expected output.
- They serve as (a) the spec you give AI, (b) the check on what comes back, (c) a guard against "AI changed the tests to pass."

```
Given a cart with 3 items and a valid 10% coupon
When the user checks out
Then total = subtotal x 0.9, rounded to 2 decimals, and the coupon is marked used
```

---

## 4. Description: The Description Chain

Goal: go from a **messy user need** to a **precise instruction AI can act on**. The outline doesn't list the chain's steps. A typical shape (inferred, verify against the lesson):

```
User need (messy)  ->  problem statement  ->  requirements / acceptance tests
                  ->  technical approach and constraints  ->  AI instruction
```
Each link removes ambiguity. If AI's output is off, find which link was vague.

A precise instruction includes:
- **Goal** and the user it serves
- **Context** (codebase, stack, existing patterns; point to files)
- **Constraints** (performance, security, dependencies, style, what not to touch)
- **Acceptance tests** (what done means)
- **Format** of the output (diff, plan first, explain trade-offs)

Tip: ask AI for a **plan** first, correct it, then implement.

---

## 5. Discernment: Five Lenses for AI-Generated Work

| Lens | Question | Check by |
|---|---|---|
| **Correctness** | Does it do the right thing, including edge cases? | Run it, acceptance tests, read the logic |
| **Quality** | Is it clean, maintainable, secure, efficient? | Code review, linters, static analysis |
| **Fit** | Does it match our codebase, conventions, architecture, and the actual need? | Compare against existing patterns and the brief |
| **Experience** | Is it good for the user to use? | Try it as a user; accessibility, clarity, flow |
| **Responsibility** | Is it safe, fair, legal, honest, privacy-respecting? | Security/privacy review, licensing, impact on users |

"It works" is the floor, not the bar. Your **taste** is the differentiator.

### Discernment for code
- Read it; don't just run it. Watch for invented APIs, unneeded dependencies, swallowed errors, weakened or deleted tests, hardcoded secrets.
- Prefer small diffs you can actually review.
- Let tests, not AI's claims, decide whether it works.

### Discernment for user experience (critiquing AI-built designs)
Feedback must be **specific enough to act on**.

| Weak | Strong |
|---|---|
| "Make it nicer" | "The primary button and the cancel link have the same weight; make Save visually dominant and move Cancel to text style." |
| "Confusing" | "Users won't know step 2 is optional; add 'Optional' label and a Skip link." |

Pattern: **observe what is there -> say what's wrong for which user -> state the change wanted.**

---

## 6. Diligence: Stand Behind What You Ship

You own the outcome, whoever or whatever wrote the code. Cover the whole arc:

| Moment | Ask |
|---|---|
| Before building | Should this exist? Who could it harm? |
| While building | Did I review it, and does it meet the bar? |
| At release | Are tests, security, privacy and rollback in place? |
| After launch | Is it serving users? What do metrics and feedback say? |

### Make the call: ship it, fix it, or stop it
| Call | When |
|---|---|
| **Ship it** | Passes acceptance tests, five lenses are acceptable, risks understood and monitored |
| **Fix it** | Close, but gaps in correctness/quality/fit/experience are named and addressable |
| **Stop it** | Wrong problem, unacceptable risk, or cost of fixing exceeds value |

Safety nets: automated tests, monitoring, staged rollouts and feature flags, a quick rollback path, and feedback loops from real users.

---

## 7. Quick Reference

| Need | Do |
|---|---|
| Stop re-explaining context | Write a reusable brief |
| Know what to hand to AI | Decompose the stages; delegate what you can verify |
| Define done | Acceptance tests before code |
| Get better output | Trace and fix the vague link in the Description Chain |
| Review AI work | Correctness, quality, fit, experience, responsibility |
| Give design feedback | Specific, user-grounded, actionable |
| Release decision | Ship / fix / stop, backed by tests and feedback |

## 8. Pitfalls
- Judging AI work by "it runs."
- Writing tests after the code, or letting AI edit tests to pass.
- Staying in the inner loop and skipping the outer one.
- Vague critique ("make it better") that AI cannot act on.
- Treating AI authorship as shifting responsibility away from you.
- Shipping without a rollback path or a post-launch feedback loop.
