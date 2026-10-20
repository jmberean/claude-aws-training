# Deploying Claude Enterprise with Confidence: Cheat Sheet

14 lessons, ~2.5 hr. The **five decisions** that shape a Claude Enterprise rollout, recorded in a rollout plan you keep. Running example in the course: Pluto, a fictional company.

> The outline gives the structure of the five decisions, not the console details. Setting names and options below are typical or inferred. Fill the specifics from the lessons and your admin console, and verify anything marked (verify).

---

## 1. The Frame

Decisions are made **in dependency order**, and most are **organization-wide, Owner-level** settings.

```
1 Structure & Identity  ->  2 Access  ->  3 Governance  ->  4 Spend  ->  5 Visibility
   who is in, how         what they get   what they may    how much it   what you can
   they sign in                           customize        can cost      measure
```

Every decision lesson uses the same three steps:
1. **Your decision**
2. **The choices you can make**
3. **If you change this later** (cost of changing your mind)

The goal: Claude becomes **infrastructure**, not a pilot that fades.

### Per-decision template (copy into your plan)
| Field | Fill in |
|---|---|
| Decision | |
| Option chosen | |
| Why (and alternatives rejected) | |
| Owner (person/team) | |
| Cost to change later | Low / Med / High |
| Depends on | |
| Review date | |

---

## 2. Owners and Prerequisites

- Name an **Owner** (org-wide settings need Owner-level access) and a backup, plus an intake path for requests (new team, new connector, spend raise).
- Gather before you start: your identity provider details, domains, list of teams/groups, security and legal requirements, budget owner, success metrics.
- Decide who signs off on each of the five decisions (IT, Security, Finance, business leads).

---

## 3. Decision 1: Structure & Identity

**Question:** How many organizations, and how do people and groups get in?

| Sub-decision | Options to weigh |
|---|---|
| **One org or many** | One org = shared admin, simpler analytics and billing. Many = hard separation (subsidiaries, regions, regulated units) but duplicated admin work |
| **Sign-in** | SSO via your identity provider; domain verification (verify) |
| **Provisioning** | Automated user/group sync (e.g. SCIM) vs manual invites (verify) |
| **Groups** | Map to teams or roles so access, spend and reporting can attach to them |

Design groups around how you'll **grant access, cap spend and report**, since later decisions hang off them.

Changing later: **High cost.** Merging or splitting organizations and reworking identity and groups touches everything downstream.

---

## 4. Decision 2: Access

**Question:** Which surfaces and connectors does each group get?

| Sub-decision | Options to weigh |
|---|---|
| **Surfaces per group** | Which Claude products/surfaces (chat apps, Claude Code, API access, etc.) go to which group (verify list) |
| **Connectors** | Which external systems Claude may reach (docs, tickets, code, data) via connectors/MCP; read-only vs write; which groups |

Guidance:
- Start with the groups most likely to get value, then widen (staged rollout).
- Treat each connector as a **data-access decision**: what can it read, who can use it, who approves it.
- Least privilege: grant a surface or connector to the group that needs it, not everyone.

Changing later: **Medium.** Granting is easy; revoking after people depend on it is disruptive.

---

## 5. Decision 3: Governance

**Question:** How are customizations governed?

"Customizations" = things users and teams create or add: shared instructions, projects, skills, custom connectors, agents/plugins (verify what applies to your plan).

| Choice | Trade-off |
|---|---|
| Open (anyone can create/share) | Fast adoption, harder to control quality and risk |
| Reviewed (approval before sharing org-wide) | Safer, slower; needs a reviewer and SLA |
| Curated (admin-published catalog only) | Consistent and safe, least flexible |

Define: who may create, who may publish org-wide, who reviews, how you retire stale or risky items.

Changing later: **Medium.** Tightening after an open period means cleaning up what already spread.

---

## 6. Decision 4: Spend

**Question:** How much can be spent, by whom, and who watches it?

| Sub-decision | Options to weigh |
|---|---|
| **Spend caps** | Org-level cap, per-group or per-user caps; hard stop vs alert |
| **Managing spend** | Who monitors, review cadence, process for raising a cap, chargeback to teams |

Guidance:
- Heavy agentic use (e.g. long autonomous coding runs) can dominate cost. Cap and watch it.
- Pair caps with **visibility** (decision 5) so you notice trends before the limit hits.
- Decide the owner who can approve increases, and how fast.

Changing later: **Low to medium.** Caps are easy to adjust; the real cost is surprising a team by lowering one.

---

## 7. Decision 5: Visibility

**Question:** What can you measure, and what signals tell you it's working?

| Sub-decision | Notes |
|---|---|
| **What you can measure** | What the analytics dashboard and any logs/audit/export options actually show (verify); what they do *not* show |
| **Adoption signals** | Active users per group, usage depth (return frequency, feature use), connector usage, spend per active user |

Guidance:
- Pick a few signals **before** launch and a target for each; otherwise you can't tell success from noise.
- Distinguish **activity** (seats used) from **value** (work changed). Pair numbers with qualitative feedback from teams.
- Know your privacy and compliance boundaries on what you collect.

Changing later: **Low.** Metrics can evolve, but you lose historical baselines you never captured.

---

## 8. How the Decisions Connect

A change in one cascades. Predict before you change.

| If you change... | It affects... |
|---|---|
| Groups (1) | Who can get surfaces/connectors (2), caps (4), and the slices you report on (5) |
| Add a connector (2) | Governance review load (3), data-risk surface, possibly spend (4) |
| Loosen governance (3) | Adoption and spend up (4), more to monitor (5) |
| Tighten spend caps (4) | Heavy users blocked, so adoption signals (5) dip and requests to Access/Owners rise |
| Change what you track (5) | What you can prove to stakeholders and when to adjust 2-4 |

Rule: when you adjust one decision, re-read the other four in the plan.

### When a new product arrives
Run it through the same five questions: Who gets it (1, 2)? Does it create customizations to govern (3)? What does it cost and who caps it (4)? How will we see adoption (5)? Add it to the plan rather than enabling it ad hoc.

---

## 9. Turning It Into the Rollout Plan

1. Fill one template row per decision (section 1).
2. Add owners and review dates.
3. Walk stakeholders through the plan at **kickoff**: decisions, reasoning, cost to change, who to ask.
4. Re-review on a schedule and whenever a new product or team arrives.

## 10. Quick Reference

| # | Decision | Core question | Change cost |
|---|---|---|---|
| 1 | Structure & Identity | One org or many? Which groups? | High |
| 2 | Access | Which surfaces/connectors per group? | Medium |
| 3 | Governance | Who creates and shares customizations? | Medium |
| 4 | Spend | What caps, who manages? | Low-Med |
| 5 | Visibility | What do we measure? | Low |

## 11. Pitfalls
- Deciding in the wrong order (caps and connectors before groups exist).
- Everything open on day one, then trying to tighten.
- Connectors enabled with no owner for the data they expose.
- No agreed success metrics, so no way to defend the rollout.
- Changing one setting without checking the cascade.
- Plan written once and never reviewed.
