# Claude with Amazon Bedrock: Cheat Sheet

65 lessons, 8 hr. Covers API, prompting, tool use, RAG, MCP, agents.

> Built from the course outline plus general Bedrock/Claude knowledge. Confirm model IDs and region prefixes in the Bedrock console, since they change.

---

## 1. Setup and the API

### Auth and access
- AWS account, region with Bedrock, and **model access enabled** for the Claude models (console: Bedrock, Model access).
- Credentials via IAM role / `aws configure` / env vars. Needs `bedrock:InvokeModel` (and `InvokeModelWithResponseStream`).
- Cross-region **inference profiles** use a prefix (`us.`, `eu.`, `global.`) on the model ID.

### Two ways to call

**A. Anthropic SDK for Bedrock** (same interface as the direct API)
```python
from anthropic import AnthropicBedrock

client = AnthropicBedrock(aws_region="us-east-1")
msg = client.messages.create(
    model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    max_tokens=512,
    system="You are a concise assistant.",
    messages=[{"role": "user", "content": "Hello"}],
)
print(msg.content[0].text)
```

**B. boto3 Converse API** (model-agnostic, unified tool-use format)
```python
import boto3
br = boto3.client("bedrock-runtime", region_name="us-east-1")
resp = br.converse(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    system=[{"text": "Be concise."}],
    messages=[{"role": "user", "content": [{"text": "Hello"}]}],
    inferenceConfig={"maxTokens": 512, "temperature": 0.0},
)
print(resp["output"]["message"]["content"][0]["text"])
```

| | AnthropicBedrock | boto3 `converse` |
|---|---|---|
| Message shape | `content` string or blocks | `content` = list of `{"text": ...}` blocks |
| Params | `max_tokens`, `temperature` | `inferenceConfig.maxTokens` ... |
| Best for | Anthropic-feature parity | Switching between providers |

### Conversation basics
- API is **stateless**: resend the full `messages` list each turn, alternating `user` / `assistant`.
- **System prompt** sets role, tone, rules; it is separate from `messages`.
- `max_tokens` caps output; **temperature** 0 for deterministic/extraction, higher for creative.
- **Prefill** (start the assistant turn) steers format, and **stop sequences** end generation early.
- **Streaming** (`messages.stream` / `converse_stream`) for responsive UIs.
- **Structured output**: ask for JSON in the prompt, prefill `{`, or force a tool schema, then parse and validate.

---

## 2. Prompt Engineering and Evals

### Prompt techniques
- Be **clear and direct**; state the task, audience, and output format.
- Give **examples** (few-shot / multishot) of the desired input to output.
- Use **XML tags** (`<document>`, `<instructions>`) to separate sections.
- Let it **think** step by step for hard reasoning (or enable extended thinking).
- Put long documents **first**, the question **last**.

### Eval workflow
1. Build a **test dataset** (inputs plus expected outputs or criteria).
2. Run the prompt over all cases.
3. **Grade**, then change one thing, re-run, compare.

| Grader | How | Use for |
|---|---|---|
| **Code-based** | Exact match, regex, JSON schema, unit checks | Objective answers, format compliance |
| **Model-based** | A (cheap) Claude scores against a rubric | Quality, tone, helpfulness |
| Human | Manual review | Calibrating the other two |

Tips: use a clear rubric, ask for reasoning before the score, and calibrate the LLM judge against human labels.

---

## 3. Tool Use

### Define a tool (JSON Schema)
```python
tools = [{
    "name": "get_weather",
    "description": "Get current weather for a city. Use when the user asks about weather.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name"}},
        "required": ["city"],
    },
}]
```
- **Description quality drives correct tool selection**: say what it does, when to use it, and what the params mean.

### The loop
```
send messages + tools
  -> stop_reason == "tool_use"?
       yes: run the tool(s), append assistant msg + user msg with tool_result
            (matching tool_use_id), call again
       no (end_turn): return final text
```
```python
while True:
    r = client.messages.create(model=M, max_tokens=512, tools=tools, messages=msgs)
    msgs.append({"role": "assistant", "content": r.content})
    if r.stop_reason != "tool_use":
        break
    results = [{"type": "tool_result", "tool_use_id": b.id, "content": run(b.name, b.input)}
               for b in r.content if b.type == "tool_use"]
    msgs.append({"role": "user", "content": results})
```

### Key points
- **Multi-turn tool use**: Claude may chain several calls before answering.
- **Batch / parallel tool calls**: one response can contain multiple `tool_use` blocks. Return **all** results in a single user message.
- Return errors in the `tool_result` (`is_error: true`) so Claude can recover.
- **Built-in / server tools** (e.g. text editor, web search, code execution, where available on Bedrock) reduce custom code.
- **Tool choice**: `auto` (default), `any` (must use a tool), or a specific tool (force structured output).

---

## 4. RAG (Retrieval Augmented Generation)

### Pipeline
```
Preprocess (once):  chunk -> embed -> store (vector DB + BM25 index)
Query (each time):  embed query -> vector search + BM25 search -> merge (RRF) -> [rerank] -> prompt Claude
```

### Chunking
| Strategy | Notes |
|---|---|
| Fixed size + overlap | Simple baseline (overlap preserves context across edges) |
| By structure (headings, paragraphs, sentences) | Better semantic integrity |
| Semantic chunking | Split on topic shifts; costlier |

### Embeddings
- Convert text to vectors; similarity (cosine) approximates meaning.
- On Bedrock use **Titan Embeddings** or **Cohere Embed**; use the **same model** for docs and queries.

### Hybrid search
- **Semantic**: conceptual matches ("training" ~ "learning").
- **BM25**: exact terms/IDs (`INC-2023-Q4-011`).
- **Reciprocal Rank Fusion**: `score(d) = Σ 1 / (k + rank_i(d))`, with k ~ 60. It uses ranks, so no score normalization is needed.

### Improving quality
- **Reranking**: a second-pass model reorders the top-N candidates, which boosts precision.
- **Multi-index architecture**: separate indexes (vector + BM25, or per source) merged at query time.
- **Contextual retrieval**: before embedding, have Claude prepend a short chunk-specific context ("This chunk is from the Q3 report, section on revenue...") so chunks stay meaningful in isolation. Pair with **prompt caching** to keep the cost low.

### Prompting the generator
- Put retrieved chunks in `<context>` tags, instruct "answer only from context; say if not found," and ask for citations.

---

## 5. Advanced Features

| Feature | What / why | Notes |
|---|---|---|
| **Extended thinking** | Claude reasons before answering | Set a thinking token budget; costs more tokens; good for math, logic, planning |
| **Vision** | Send images as content blocks (base64) | Charts, screenshots, documents; keep images clear and sized reasonably |
| **Prompt caching** | Cache a large static prefix (system prompt, docs, tools) | Cheaper and faster repeats; put stable content first and mark the cache breakpoint |
| **Streaming** | Token-by-token output | UX latency |
| **Temperature** | Randomness | 0 for extraction/grading |
| **Batch inference** | Async bulk jobs at discounted price | Offline evals, large-scale processing |

---

## 6. Model Context Protocol (MCP)

### What it is
A standard protocol so apps can plug into tools/data without bespoke integrations. **Client** (your app / the model host) talks to **servers** (expose capabilities).

### Three primitives

| Primitive | Controlled by | Purpose |
|---|---|---|
| **Tools** | Model | Actions Claude can call (e.g. `edit_document`) |
| **Resources** | App | Read-only data exposed by URI (e.g. `docs://list`) |
| **Prompts** | User | Reusable prompt templates |

### Server (Python `mcp` SDK, FastMCP style)
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("DocumentMCP")

@mcp.tool(name="read_doc_contents", description="Read a document by ID")
def read_doc_contents(doc_id: str) -> str:
    return docs[doc_id]

@mcp.resource("docs://documents")
def list_docs() -> list[str]:
    return list(docs)

@mcp.prompt(name="format")
def format_doc(doc_id: str): ...

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Client lifecycle
1. Launch/connect server (stdio subprocess or HTTP).
2. **Initialize** handshake.
3. `list_tools` / `list_resources` / `list_prompts`.
4. Pass tool definitions to Claude; when Claude emits `tool_use`, call `session.call_tool(name, args)` and return the result.
5. Clean up the session.

### Tips
- **MCP Inspector** (`mcp dev server.py`) tests a server interactively.
- A script that imports server code directly is *not* an MCP client; a real one speaks the protocol (JSON-RPC over stdio/HTTP).
- Transports: **stdio** (local) vs **streamable HTTP** (remote).

---

## 7. Agents

### Workflows vs agents
- **Workflow**: fixed, predefined steps (chaining, routing, parallelization). Predictable.
- **Agent**: Claude decides next steps in a loop with tools. Flexible, less predictable.
- Prefer the simplest thing that works: workflow first, agent only when the path is unknowable up front.

### Claude Code
- Agentic coding assistant for automated debugging and task execution; extensible via MCP servers.

### Computer Use
- Claude controls a UI through screenshots plus mouse/keyboard actions (`computer`, `text_editor`, `bash` tools).
- Run inside a **sandboxed VM/container**; it is slower and less reliable than API tools, so use it only when no API exists.

### Agent design tips
- Give clear tool descriptions, bounded loops (max iterations), and good error messages.
- Log every tool call for debugging; add human checkpoints for destructive actions.

---

## 8. Cost and Production Checklist

- Start with **Haiku**; upgrade only if evals show a quality gap.
- Keep `max_tokens` low in tests (256-512).
- Use prompt caching for repeated prefixes; batch inference for offline jobs.
- Handle `ThrottlingException` with exponential backoff and retries.
- Least-privilege IAM; never hardcode credentials.
- Use Bedrock **Guardrails** for content filtering where required.
- Monitor via CloudWatch metrics and invocation logging.
- Build an eval set **before** tuning prompts.

## 9. Quick Reference

| Need | Use |
|---|---|
| Simple call | `AnthropicBedrock().messages.create` |
| Provider-agnostic | boto3 `converse` |
| Structured JSON | Forced tool schema or prefill `{` |
| Call external functions | Tools + `tool_result` loop |
| Ground in documents | RAG: hybrid search + RRF (+ rerank) |
| Better chunk recall | Contextual retrieval |
| Hard reasoning | Extended thinking |
| Big repeated prompt | Prompt caching |
| Modular tool ecosystem | MCP |
| Open-ended multi-step | Agent loop |
