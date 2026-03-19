# Example Files

The repository includes two example files that demonstrate how to build MCP servers and clients.

## OneMCPServer.py — Demo MCP Server

A minimal MCP server built with `FastMCP`. Use it to test MCPRegistry without needing an external server.

### Running it

```bash
# With uv (matches the Demo saved server config)
uv run OneMCPServer.py

# With Python directly
python OneMCPServer.py
```

### Exposed tools

| Tool | Signature | Description |
|------|-----------|-------------|
| `add` | `add(a: int, b: int) -> int` | Returns `a + b` |
| `multiply` | `multiply(a: int, b: int) -> int` | Returns `a * b` |

### Exposed resources

| Resource URI | Handler | Description |
|--------------|---------|-------------|
| `greeting://{name}` | `get_greeting(name)` | Returns `"Hello, {name}!"` |

### Code reference

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == '__main__':
    mcp.run()
```

---

## OneMCPClient.py — Demo MCP Client

An async Python script showing how to connect to an MCP server over stdio and list its capabilities. This is a standalone reference — it is not used by the MCPRegistry UI.

### Running it

```bash
# Start the server first
uv run OneMCPServer.py

# In another terminal
python OneMCPClient.py
```

### What it does

1. Creates `StdioServerParameters` to launch `OneMCPServer.py` via `python`.
2. Defines an optional `handle_sampling_message` callback (returns a dummy model response).
3. Opens a `stdio_client` context and a `ClientSession`.
4. Calls:
   - `session.list_prompts()` — list available prompts
   - `session.list_resources()` — list available resources
   - `session.list_tools()` — list available tools (printed to stdout)

### Extending the example

Uncomment the relevant lines in `OneMCPClient.py` to:
- Retrieve a specific prompt: `session.get_prompt("name", arguments={...})`
- Read a resource: `session.read_resource("file://some/path")`
- Call a tool: `session.call_tool("tool-name", arguments={...})`
