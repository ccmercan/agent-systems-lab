# toy_agent.py

import json
from toy_mcp_server import handle_mcp_request

# 1. Discover tools
discover_request = json.dumps({"type": "list_tools"})
discover_response = handle_mcp_request(discover_request)
tools = json.loads(discover_response)

print("Discovered tools:")
print(json.dumps(tools, indent=2))


# 2. Decide to call a tool (simulated reasoning)
call_request = json.dumps({
    "type": "call_tool",
    "tool": "add_numbers",
    "args": {
        "a": 3,
        "b": 5
    }
})

call_response = handle_mcp_request(call_request)
result = json.loads(call_response)

print("\nTool result:")
print(result)
