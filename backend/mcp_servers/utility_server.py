from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Universal Agent Utility Server",
    host="127.0.0.1",
    port=8001
)

@mcp.tool()
def get_system_info() -> dict:
    """Get basic information about the operating system."""

    import platform

    return {
        "operating_system": platform.system(),
        "platform": platform.platform(),
        "python_version": platform.python_version()
    }


@mcp.tool()
def calculate(expression: str) -> str:
    """Evaluate a basic mathematical expression."""

    import ast
    import operator

    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv
    }

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in operators:
            return operators[type(node.op)](
                evaluate(node.left),
                evaluate(node.right)
            )

        raise ValueError("Unsupported mathematical expression")

    try:
        tree = ast.parse(expression, mode="eval")
        return str(evaluate(tree.body))
    except Exception as error:
        return f"Calculation error: {error}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")