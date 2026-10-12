# Model Context Protocol: Advanced Topics: Cheat Sheet

11 lessons, ~1.5 hr. Sampling, notifications/progress, roots, and transports (STDIO, StreamableHTTP).

> Built from the course outline plus general MCP knowledge. Parameter names (callbacks, `stateless_http`, `json_response`) follow the common Python SDK API. This repo has `mcp` 2.x installed, so confirm names against your version.

---

## 1. Core Features

### Sampling (server asks the client's LLM)
- A server needs an LLM call (summarize, classify) but has no model access or API key.
- Server sends a `sampling/createMessage` request **to the client**; the client calls its own model and returns the result.
- **Why**: shifts AI cost, API keys, and complexity from server to client. The server stays lightweight and model-agnostic.

```python
# Server tool: asks the connected client's model
@mcp.tool()
async def summarize(text: str, ctx: Context) -> str:
    result = await ctx.session.create_message(
        messages=[SamplingMessage(role="user",
                  content=TextContent(type="text", text=f"Summarize: {text}"))],
        max_tokens=300,
    )
    return result.content.text
```
```python
# Client: provide the callback that actually calls Claude
async def sampling_callback(context, params):
    reply = anthropic_client.messages.create(
        model="claude-haiku-4-5", max_tokens=params.maxTokens or 300,
        messages=[{"role": "user", "content": params.messages[0].content.text}])
    return CreateMessageResult(role="assistant", model="claude-haiku-4-5",
                               content=TextContent(type="text", text=reply.content[0].text))

ClientSession(read, write, sampling_callback=sampling_callback)
```
- Client should be able to review/deny sampling requests (human in the loop).
- Requires a **bidirectional** connection (see transports).

### Context object (logging + progress)
Add a `ctx: Context` parameter to a tool and the SDK injects it.

```python
@mcp.tool()
async def process(files: list[str], ctx: Context) -> str:
    await ctx.info("Starting")                    # log message -> client
    for i, f in enumerate(files):
        await ctx.report_progress(i + 1, len(files))   # progress update
        ...
    await ctx.warning("Done with warnings")
    return "ok"
```
| Method | Purpose |
|---|---|
| `ctx.debug/info/warning/error(msg)` | Log notifications to the client |
| `ctx.report_progress(progress, total)` | Progress notification for long operations |

```python
# Client: receive them
async def logging_callback(params):
    print(f"[{params.level}] {params.data}")

async def progress_callback(progress, total, message):
    print(f"{progress}/{total}")

ClientSession(read, write, logging_message_callback=logging_callback)
await session.call_tool("process", {...}, progress_callback=progress_callback)
```
- Use for anything long-running so the UI is not a silent spinner.

### Roots (scoped file access)
- Client tells the server which **directories** it may work in (`file://` URIs).
- Security boundary: server should only touch paths under granted roots.
- UX benefit: server can discover files in those roots instead of asking the user for full paths.

```python
# Client: declare roots
async def list_roots_callback(context):
    return ListRootsResult(roots=[Root(uri="file:///Users/me/project", name="project")])
ClientSession(read, write, list_roots_callback=list_roots_callback)

# Server: ask for them, then enforce
roots = await ctx.session.list_roots()
# validate: resolved path must be inside one of roots.roots[*].uri
```
- Roots are a **guideline the server must honor**, not an OS-level sandbox. Validate paths (resolve `..`, symlinks) in server code.

---

## 2. Message Types

| Kind | Has `id`? | Response? | Examples |
|---|---|---|---|
| **Request** | yes | yes (result or error) | `tools/call`, `resources/read`, `sampling/createMessage`, `roots/list` |
| **Notification** | no | no (fire-and-forget) | `notifications/progress`, `notifications/message`, `notifications/initialized`, `notifications/tools/list_changed` |

- Format is **JSON-RPC 2.0**.
- **Bidirectional**: clients send requests (tool calls); servers also send requests (sampling, roots) and notifications (progress, logs).

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"process","arguments":{}}}
{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"ok"}]}}
{"jsonrpc":"2.0","method":"notifications/progress","params":{"progress":3,"total":10}}
```

---

## 3. Transports

### STDIO (local)
- Client launches the server as a **subprocess**; JSON messages over stdin/stdout.
- Great for local dev and desktop tools; no networking, no auth setup.
- **Never print to stdout** in the server (corrupts the stream); log to stderr.
- Required **initialization handshake**:

```
Client -> Server : initialize (request: protocol version, client capabilities)
Server -> Client : result (server capabilities, version)
Client -> Server : notifications/initialized
... normal traffic ...
```
- Both sides can send requests/notifications any time after the handshake.

### StreamableHTTP (remote)
- Server runs as an HTTP service; many clients connect.
- Client -> server: **HTTP POST** per message.
- Server -> client: **Server-Sent Events (SSE)** stream (needed for sampling, roots, progress, logs).
- **Dual-connection model**: POST requests for client messages plus a separate long-lived SSE stream (GET) for server-initiated messages.
- **Sessions**: server issues a session ID (`Mcp-Session-Id` header) at initialize; client sends it on every request so the server can route to the right state/stream.

### Config flags that change behavior
| Flag | Effect |
|---|---|
| `stateless_http=True` | No session tracking; each request is independent |
| `json_response=True` | Return plain JSON instead of opening an SSE stream |

```python
mcp = MCPServer("MyServer", stateless_http=True, json_response=True)
mcp.run(transport="streamable-http")
```

### Stateful vs stateless HTTP

| | Stateful (default) | Stateless |
|---|---|---|
| Session state kept | yes | no |
| Server-initiated requests (sampling, roots) | works | **not available** |
| Progress/log streaming | works | **limited/unavailable** |
| Load balancing | needs sticky sessions | **any instance can serve any request** |
| Horizontal scaling | harder | easy |
| Best for | rich, interactive features | high-scale simple tool servers |

Trade-off: stateless gives up server->client features to scale behind a load balancer.

---

## 4. Choosing a Transport

```
Local, single user, dev/desktop?          -> STDIO
Remote, needs sampling/roots/progress?    -> StreamableHTTP, stateful
Remote, high scale, simple tools only?    -> StreamableHTTP, stateless (+ json_response)
Stateful but many instances?              -> sticky sessions or shared session store
```

---

## 5. Quick Reference

| Need | Use |
|---|---|
| Server needs an LLM, has no key | Sampling (`ctx.session.create_message`) |
| Show log lines to the user | `ctx.info/warning/error` + `logging_message_callback` |
| Progress bar for long tool | `ctx.report_progress` + `progress_callback` |
| Restrict file access | Roots (`list_roots_callback`; validate paths) |
| Local server | STDIO |
| Remote server | StreamableHTTP |
| Scale behind load balancer | `stateless_http=True` |
| Avoid SSE streams | `json_response=True` |

## 6. Pitfalls
- Enabling `stateless_http` and then expecting sampling/roots/progress to work.
- Treating roots as enforcement; the server must check paths itself.
- Skipping the `initialize` -> `initialized` handshake in a hand-rolled client.
- Writing to stdout in a STDIO server.
- Auto-approving sampling requests with no client-side review or cost cap.
- Load-balancing stateful HTTP without sticky sessions (session ID lands on the wrong instance).
