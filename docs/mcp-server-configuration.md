# MCP Server Configuration

Server configurations are stored in `mcp_servers.json` at the project root. The file is a JSON object where each key is the server's display name.

## Schema

### HTTP Server

```json
{
  "ServerName": {
    "protocol": "http",
    "url": "http://localhost:8000"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `protocol` | string | yes | Must be `"http"` |
| `url` | string | yes | Base URL of the MCP server |

### stdio Server

```json
{
  "ServerName": {
    "protocol": "stdio",
    "command": "uv",
    "program": ["run", "OneMCPServer.py"]
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `protocol` | string | yes | Must be `"stdio"` |
| `command` | string | yes | Executable to run (e.g. `uv`, `python`, `node`) |
| `program` | string or array | yes | Arguments passed to the command |

## Default Configuration

The repository ships with a single pre-configured server:

```json
{
  "Demo": {
    "protocol": "stdio",
    "command": "uv",
    "program": ["run", "OneMCPServer.py"]
  }
}
```

This connects to the bundled `OneMCPServer.py` demo using `uv`.

## Adding Servers Manually

You can edit `mcp_servers.json` directly to add multiple servers at once:

```json
{
  "Demo": {
    "protocol": "stdio",
    "command": "uv",
    "program": ["run", "OneMCPServer.py"]
  },
  "MyHTTPServer": {
    "protocol": "http",
    "url": "http://localhost:9000"
  },
  "MyPythonServer": {
    "protocol": "stdio",
    "command": "python",
    "program": ["my_mcp_server.py"]
  }
}
```

Changes to `mcp_servers.json` take effect on the next app reload (or when the saved servers are re-loaded from the Manage Servers tab).

## Adding Servers via the UI

Use the **Manage Servers** tab to add servers without editing JSON directly. See the [User Guide](user-guide.md#adding-a-new-server) for step-by-step instructions.
