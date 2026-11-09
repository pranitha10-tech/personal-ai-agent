
import asyncio

from mcp_servers.mcp_registry import execute_tool


async def main():

    # Test 1: Get system information
    print("\n===== TEST 1: SYSTEM INFORMATION =====")

    result = await execute_tool("get_system_info", {})

    for item in result.content:
        if hasattr(item, "text"):
            print(item.text)


    # Test 2: Calculator
    print("\n===== TEST 2: CALCULATOR =====")

    result = await execute_tool(
        "calculate",
        {"expression": "25 + 15 * 2"}
    )

    for item in result.content:
        if hasattr(item, "text"):
            print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
