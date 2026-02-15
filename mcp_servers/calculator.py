"""
Minimal MCP server that exposes a calculator tool over stdio.

Run with: python -m mcp_servers.calculator

Used by the agent via langchain-mcp-adapters (stdio transport).
"""

import re
import anyio
import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server


def _safe_eval(expression: str) -> float:
    """Evaluate a simple math expression (numbers, +, -, *, /, parentheses)."""
    expression = expression.strip()
    if not re.match(r"^[\d\s+\-*/().]+$", expression):
        raise ValueError("Only numbers and + - * / ( ) are allowed")
    try:
        return float(eval(expression))
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}") from e


def main() -> int:
    server = Server("calculator")

    @server.list_tools()
    async def handle_list_tools(_request: types.ListToolsRequest) -> types.ListToolsResult:
        return types.ListToolsResult(
            tools=[
                types.Tool(
                    name="calculate",
                    description="Evaluate a math expression. Use only numbers and operators: + - * / ( ). Example: (2 + 3) * 4",
                    inputSchema={
                        "type": "object",
                        "required": ["expression"],
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Math expression to evaluate, e.g. '2 + 3 * 4' or '(10 - 2) / 4'",
                            },
                        },
                    },
                ),
            ]
        )

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict | None) -> types.CallToolResult:
        if name != "calculate":
            raise ValueError(f"Unknown tool: {name}")
        args = arguments or {}
        if "expression" not in args:
            raise ValueError("Missing required argument: expression")
        try:
            result = _safe_eval(str(args["expression"]))
            if isinstance(result, float) and result.is_integer():
                text = str(int(result))
            else:
                text = str(result)
        except ValueError as e:
            text = f"Error: {e}"
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
