# Introduction to Model Context Protocol: Cheat Sheet

10 lessons, ~1 hr. Build MCP servers and clients with the Python SDK: tools, resources, prompts.

> Built from the course outline plus general MCP knowledge. The SDK moves fast: this repo has `mcp` 2.x installed (`MCPServer`), while most tutorials use 1.x (`FastMCP`). Check the import path and client API against your installed version.

---

## 1. Why MCP

- Without MCP, **you** write and maintain tool schemas + execution code for every service (GitHub, Slack, DBs...).
- With MCP, a specialized **MCP server** owns the tool definitions and execution; your app just connects as a **client**.
- Shifts the burden from your app to server authors, and servers are reusable across apps and models.

```
User -> Your app (MCP client) -> MCP server -> External service (API/DB/files)
                  |                  |
                  +-- tool list ---> Claude    <- results flow back the same path
```

### Architecture terms
| Term | Meaning |
|---|---|
| **Host** | The app the user talks to (your chat app, Claude Code) |
| **Client** | Connection object inside the host; one client per server |
| **Server** | Process exposing tools / resources / prompts |
| **Transport** | How messages travel (stdio, HTTP) |

### Transport and messages
- **Transport-agnostic**: same protocol over **stdio** (local subprocess), **streamable HTTP** (remote), or others.
- Messages are **JSON-RPC 2.0**: requests (expect a response), responses, notifications (fire-and-forget).
- Lifecycle: `initialize` handshake -> list capabilities -> calls -> shutdown.
- Typical methods: `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list`, `prompts/get`.

### Request flow (one user query)
1. User asks a question in the app.
2. Client sends `tools/list` to the server; app passes those definitions to Claude.
3. Claude replies with a `tool_use` block.
4. Client sends `tools/call` to the server.
5. Server runs the action against the external service and returns the result.
6. App sends the result back to Claude as a `tool_result`; Claude writes the final answer.

---

## 2. Build a Server (Python SDK)

Decorators replace hand-written JSON Schema: **type hints + `Field` descriptions generate the schema**.

```python
from mcp.server.mcpserver import MCPServer   # mcp 2.x (this repo)
# from mcp.server.fastmcp import FastMCP     # mcp 1.x equivalent
from pydantic import Field

mcp = MCPServer("DocumentMCP")
docs = {"plan.md": "Q3 plan...", "notes.txt": "Meeting notes..."}

@mcp.tool(name="read_doc_contents", description="Read a document by ID")
def read_doc_contents(
    doc_id: str = Field(description="ID of the document to read")
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc '{doc_id}' not found")
    return docs[doc_id]

@mcp.tool(name="edit_document", description="Find-and-replace edit on a document")
def edit_document(
    doc_id: str = Field(description="Document ID"),
    old_str: str = Field(description="Exact text to replace"),
    new_str: str = Field(description="Replacement text"),
) -> str:
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return "ok"

if __name__ == "__main__":
    mcp.run()          # defaults to stdio
```

Tool-writing rules:
- Clear `description` on the tool **and** each `Field`: this is what Claude reads to choose and fill args.
- Type hints define the schema (`str`, `int`, `list[str]`, `Optional[...]`).
- **Raise errors with helpful messages** (list valid IDs, say what to fix) so Claude can self-correct.
- Return strings/JSON-serializable data.

---

## 3. Test with the Inspector

```bash
mcp dev server.py        # opens browser-based MCP Inspector
# or: npx @modelcontextprotocol/inspector python server.py
```
- Connect, then use the **Tools / Resources / Prompts** tabs to list and invoke primitives with test inputs.
- Check: schema looks right, descriptions render, errors are readable. Fix before wiring to Claude.
- Debug tip for stdio servers: never `print()` to stdout (it corrupts the protocol); log to **stderr**.

---

## 4. The Three Primitives

| Primitive | Controlled by | Purpose | Example |
|---|---|---|---|
| **Tools** | **Model** (Claude decides) | Actions / computation | `edit_document` |
| **Resources** | **App** (your code decides) | Read-only data exposed by URI | `docs://documents` |
| **Prompts** | **User** (user triggers) | Pre-crafted instruction templates | `/format` command |

Use which?
- Claude should decide to do something -> **tool**
- Your app needs to fetch data to show/inject (autocomplete lists, context) -> **resource**
- User wants a polished, tested workflow on demand -> **prompt**

### Resources
```python
@mcp.resource("docs://documents", mime_type="application/json")   # direct: static URI
def list_docs() -> list[str]:
    return list(docs.keys())

@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")  # templated: URI params
def fetch_doc(doc_id: str) -> str:
    return docs[doc_id]
```
| Type | URI | Notes |
|---|---|---|
| Direct | static, `docs://documents` | Same data each time |
| Templated | `docs://documents/{doc_id}` | Params become function args |

- Set **`mime_type`** so clients parse correctly: `application/json` or `text/plain`.

### Prompts
```python
from mcp.server.mcpserver.prompts import base   # path may differ by version

@mcp.prompt(name="format", description="Rewrite a document in Markdown")
def format_document(doc_id: str = Field(description="Document to format")) -> list[base.Message]:
    return [base.UserMessage(f"Reformat document `{doc_id}` as clean Markdown. "
                             "Use the read tool, then the edit tool.")]
```
- Returns a list of messages the client injects into the conversation.
- Value: one expert-written prompt reused by everyone, versus each user improvising.

---

## 5. Build a Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command="python", args=["mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()                          # handshake

            tools = (await session.list_tools()).tools          # -> give to Claude
            result = await session.call_tool("read_doc_contents",
                                             {"doc_id": "plan.md"})
            print(result.content[0].text)

            res = await session.read_resource("docs://documents")  # resource
            prompts = await session.list_prompts()
            p = await session.get_prompt("format", {"doc_id": "plan.md"})

asyncio.run(main())
```

### Resource reading and MIME types
```python
import json
r = (await session.read_resource(uri)).contents[0]
data = json.loads(r.text) if r.mimeType == "application/json" else r.text
```

### Wiring tools to Claude
1. `list_tools()` -> convert each to `{name, description, input_schema}` for the Messages API.
2. On `stop_reason == "tool_use"`, call `session.call_tool(block.name, block.input)`.
3. Return the output as a `tool_result` with the matching `tool_use_id`.

---

## 6. Integration Patterns

- **Autocomplete**: client reads the resource list (e.g. all doc IDs) and offers `@doc` completions in the UI.
- **Context injection**: when a user mentions `@plan.md`, the app reads the resource and inserts its contents into the prompt, so Claude skips an extra tool round-trip.
- **Slash commands**: client lists prompts and exposes each as `/name`; running it calls `get_prompt` and sends the returned messages.

---

## 7. Quick Reference

| Task | Code |
|---|---|
| Create server | `mcp = MCPServer("Name")` |
| Define tool | `@mcp.tool(name=..., description=...)` |
| Describe arg | `param: str = Field(description="...")` |
| Direct resource | `@mcp.resource("scheme://path", mime_type=...)` |
| Templated resource | `@mcp.resource("scheme://path/{id}")` |
| Define prompt | `@mcp.prompt(name=..., description=...)` |
| Run server | `mcp.run()` |
| Inspector | `mcp dev server.py` |
| Client connect | `stdio_client` + `ClientSession` + `initialize()` |
| Call tool | `session.call_tool(name, args)` |
| Read resource | `session.read_resource(uri)` |
| Get prompt | `session.get_prompt(name, args)` |

## 8. Pitfalls
- `print()` to stdout in a stdio server breaks the protocol (use stderr or logging).
- Vague tool/Field descriptions lead to wrong tool choice or bad arguments.
- Forgetting `await session.initialize()` before other calls.
- Missing/wrong `mime_type` on resources, so clients mis-parse JSON.
- Treating a script that imports server code as a client: a real client speaks the protocol.
- In-memory state (like the `docs` dict) resets every time the server restarts.
