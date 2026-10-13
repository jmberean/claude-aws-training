# AI Fluency: Framework and Foundations: Cheat Sheet

14 lessons, ~4 hr (marked "skim" in the plan). Collaborating with AI **effectively, efficiently, ethically, and safely** via the 4D Framework. Created by Rick Dakan and Joseph Feller with Anthropic.

> Built from the course outline plus general knowledge of the framework. Sub-point wording may differ slightly from the lessons.

---

## 1. The Big Picture

**AI Fluency** = working with AI well, beyond "cool prompts," in a way that holds up as models and tools change.

### The 4Ds
```
Delegation  -> decide WHAT to do with AI, and which AI
Description -> tell the AI clearly what you want and how
Discernment -> evaluate what comes back
Diligence   -> take responsibility for the work and its use
```
Description and Discernment feed each other in a loop (section 5).

### Three modes of engaging with AI
| Mode | Meaning | Example |
|---|---|---|
| **Automation** | AI does a defined task you specify | "Reformat these 200 citations" |
| **Augmentation** | You and AI work as thinking partners, back and forth | Brainstorming, drafting, critiquing together |
| **Agency** | AI acts independently on your behalf, with your setup of its goals and behavior | An agent that triages issues or runs a workflow |

Pick the mode per task. Agency needs the most up-front design and the most Diligence.

---

## 2. Generative AI Fundamentals

- **LLMs** are trained on huge text corpora to predict the next token, which gives fluent, flexible output.
- Strengths: drafting, summarizing, transforming, explaining, coding, brainstorming, working across formats and languages.
- Output is **probabilistic**: the same prompt can yield different answers.

### Capabilities and limitations
| Limitation | What it means for you |
|---|---|
| **Hallucination** | Can state false things confidently; verify facts |
| **Knowledge cutoff** | Doesn't know recent events without tools or context |
| **Limited context window** | Can lose or ignore parts of very long inputs |
| **No persistent memory** by default | Doesn't remember past chats unless given context |
| **Sensitivity to phrasing** | Small prompt changes can change results |
| **Reasoning gaps** | Can fail at precise math or multi-step logic without help |
| **Bias** | Reflects patterns and gaps in its training data |

---

## 3. Delegation: What to hand to AI

Three awarenesses:

| Awareness | Question | Think about |
|---|---|---|
| **Problem Awareness** | What am I actually trying to achieve? | Goal, scope, success criteria, what "good" looks like |
| **Platform Awareness** | Which AI and what can it do? | Strengths, limits, tools, cost, data privacy of each system |
| **Task Delegation** | How do we split the work? | Who does what: human, AI, or both |

### Delegation decision checklist
- Is this a good fit for AI's strengths (and not its weaknesses)?
- What's the cost of an error here? (High stakes -> more human involvement.)
- Can I verify the output cheaply?
- Is the data safe to share with this platform?
- Which parts need human judgment, creativity, or accountability?

### Project planning
Define the goal first, break the project into tasks, assign each task to human / AI / both, and choose the mode (automation / augmentation / agency) per task.

---

## 4. Description: Telling the AI what you want

Three kinds of description:

| Type | You specify | Example |
|---|---|---|
| **Product Description** | The output: format, audience, length, tone, content, constraints | "A 300-word email to non-technical executives, plain language, ending with a clear ask" |
| **Process Description** | How the AI should approach it: steps, method, what to consider | "First list assumptions, then compare two options, then recommend" |
| **Performance Description** | How the AI should *behave* in the collaboration | "Push back on my reasoning; ask clarifying questions before answering; be concise" |

### Effective prompting techniques
| Technique | Do this |
|---|---|
| **Give context** | Background, audience, purpose, what you've tried |
| **Show examples** | Provide sample inputs/outputs of what good looks like (few-shot) |
| **Specify constraints and format** | Length, structure, things to avoid |
| **Break complex tasks into steps** | Chain smaller prompts or ask for a step-by-step plan |
| **Ask it to reason step by step** | Improves multi-step problems |
| **Assign a role/perspective** | "Act as a skeptical reviewer" |
| **Invite questions** | "Ask me what you need to know before starting" |
| **Iterate** | Treat the first answer as a draft |

---

## 5. Discernment and the Description-Discernment Loop

Evaluate three things:

| Type | Ask |
|---|---|
| **Product Discernment** | Is the output accurate, relevant, appropriate, coherent, complete? |
| **Process Discernment** | Was the reasoning sound? Did it skip steps, invent sources, or go in circles? |
| **Performance Discernment** | Did it behave as requested in the interaction (tone, honesty, following instructions)? |

### The loop
```
Describe -> AI produces -> Discern (what's wrong/missing?) -> Re-describe better -> ...
```
- Each round of evaluation tells you **what to add to your description** (more context, an example, a constraint).
- Be a critical reader: check facts, sources, logic, and tone; don't accept polished-sounding text as correct.
- Know when to stop: the output meets your criteria, or the task needs a different approach or a human.

---

## 6. Diligence: Taking responsibility

| Diligence | Focus | Key questions |
|---|---|---|
| **Creation Diligence** | Choices when building with AI | Which AI/tool? Is it appropriate and safe for this task and data? |
| **Transparency Diligence** | Honesty about AI's role | Who needs to know AI was used? Disclose appropriately. |
| **Deployment Diligence** | Responsibility for what you release | Have I verified it? Am I accountable for the consequences? |

Principles:
- You own the output, whatever tool helped produce it.
- Disclose AI involvement where trust, rules, or norms require it.
- Verify before you share or act, in proportion to the stakes.
- Protect privacy and confidential data; follow organizational policy.
- Watch for bias and harm in what you deploy.

---

## 7. Quick Reference

| Phase | Core question |
|---|---|
| Delegation | Should AI do this, which AI, and how do we split it? |
| Description | Have I specified product, process, and performance? |
| Discernment | Is the product good, was the process sound, did it behave right? |
| Diligence | Did I choose well, disclose honestly, and verify before deploying? |

### One-line prompt template
"Context: ___. Task: ___. Audience/format: ___. Constraints: ___. Approach: ___. Ask me questions first if unclear."

## 8. Pitfalls
- Delegating the thinking along with the typing.
- Vague prompts, then blaming the model.
- Trusting fluent output without checking it.
- Hiding AI use where disclosure matters.
- Sharing sensitive data with a platform you haven't vetted.
- Using agency mode with no guardrails or review.
