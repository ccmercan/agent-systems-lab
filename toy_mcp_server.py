# toy_mcp_server.py

import json

def add_numbers(a: int, b: int) -> int:
    return a + b


TOOLS = {
    "add_numbers": {
        "description": "Add two integers",
        "input_schema": {
            "a": "int",
            "b": "int"
        },
        "handler": add_numbers
    }
}


def handle_mcp_request(request_json: str) -> str:
    """
    Simulates an MCP server handling a request.
    """
    request = json.loads(request_json)

    if request["type"] == "list_tools":
        return json.dumps({
            "tools": {
                name: {
                    "description": tool["description"],
                    "input_schema": tool["input_schema"]
                }
                for name, tool in TOOLS.items()
            }
        })

    if request["type"] == "call_tool":
        tool_name = request["tool"]
        args = request["args"]

        if tool_name not in TOOLS:
            return json.dumps({"error": "Unknown tool"})

        result = TOOLS[tool_name]["handler"](**args)
        return json.dumps({"result": result})

    return json.dumps({"error": "Invalid request"})
