import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP(
    "Taiga MCP Server",
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", "8000")),
    streamable_http_path="/mcp",
)


def _build_taiga_client():
    from Functions.Taiga.client import TaigaClient

    base_url = os.getenv("TAIGA_BASE_URL")
    if not base_url:
        raise RuntimeError("TAIGA_BASE_URL is not set in the environment / .env file.")

    token = os.getenv("TAIGA_TOKEN")
    if token:
        client = TaigaClient(base_url)
        client.set_token(token)
        return client

    username = os.getenv("TAIGA_USERNAME")
    password = os.getenv("TAIGA_PASSWORD")
    if not username or not password:
        raise RuntimeError(
            "Set either TAIGA_TOKEN or both TAIGA_USERNAME and TAIGA_PASSWORD in .env."
        )

    return TaigaClient(base_url, username=username, password=password)


try:
    taiga_client = _build_taiga_client()
    from Functions.Taiga.tools import register_tools
    register_tools(mcp, taiga_client)
except Exception as e:
    import sys
    print(f"Taiga client init failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
