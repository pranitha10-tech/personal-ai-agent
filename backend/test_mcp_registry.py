
import asyncio

from mcp_servers.mcp_registry import discover_tools


async def main():
    tools = await discover_tools()

    print("\nDiscovered MCP Tools:")
    print("---------------------")

    for tool in tools:
        print(f"\nTool Name: {tool['name']}")
        print(f"Description: {tool['description']}")
        print(f"Input Schema: {tool['input_schema']}")


if __name__ == "__main__":
    asyncio.run(main())
