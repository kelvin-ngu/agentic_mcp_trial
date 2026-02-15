"""
Minimal MCP server that exposes a weather tool over stdio (mock data).

Run with: python -m mcp_servers.weather

Used by the agent via langchain-mcp-adapters (stdio transport).
"""

import anyio
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server


def _get_weather_mock(location: str) -> str:
    """Return mock weather for any location (no API key required)."""
    loc = (location or "Unknown").strip() or "Unknown"
    return (
        f"Weather in {loc}: 72°F (22°C), partly cloudy. "
        "Mock data — use a real weather MCP server or API for live data."
    )


def main() -> int:
    server = Server("weather")

    @server.list_tools()
    async def handle_list_tools(_request: types.ListToolsRequest) -> types.ListToolsResult:
        return types.ListToolsResult(
            tools=[
                types.Tool(
                    name="get_weather",
                    description="Get current weather for a location (city name or place). This demo returns mock data.",
                    inputSchema={
                        "type": "object",
                        "required": ["location"],
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City or place name, e.g. 'San Francisco' or 'London'",
                            },
                        },
                    },
                ),
            ]
        )

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict | None) -> types.CallToolResult:
        if name != "get_weather":
            raise ValueError(f"Unknown tool: {name}")
        args = arguments or {}
        location = args.get("location", "")
        text = _get_weather_mock(location)
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=text)],
            isError=False,
        )

    async def arun() -> None:
        async with stdio_server() as (read_stream, write_stream):
            init_options = server.create_initialization_options(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            )
            await server.run(read_stream, write_stream, init_options)

    anyio.run(arun)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
