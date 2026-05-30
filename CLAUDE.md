# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bat
python -m venv .venv
.venv\Scripts\activate && pip install -r requirements.txt
```

## Running the Server

```bat
.venv\Scripts\activate
python Server.py
```

Or use the provided batch files:
- `InstallRequirments.bat` — creates venv and installs dependencies
- `LauncheServer.bat` — activates the venv (run `python Server.py` after)

## Architecture

This is a [FastMCP](https://github.com/jlowin/fastmcp) server. The single dependency is the `mcp` package.

- **`Server.py`** — entry point; instantiates `FastMCP` and registers all tools via `@mcp.tool()` decorators, then calls `mcp.run()`.
- **`Functions/`** — intended location for tool implementations, organized by domain (`Taiga/`, `Other/`). Currently empty; add modules here and import them into `Server.py`.

## Adding Tools

Decorate any function with `@mcp.tool()` and it becomes available to MCP clients. All tools should be either defined directly in `Server.py` or imported from `Functions/` submodules.

```python
@mcp.tool()
def my_tool(param: str) -> str:
    """Docstring becomes the tool description shown to clients."""
    return result
```
