

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from fastapi import Header, Depends
from typing import Optional



API_KEY = "supersecretkey"
app = FastAPI(title="Toy MCP Server")
def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ------------------
# Tool definitions
# ------------------
def validate_args(tool_name: str, args: dict):
    schema = TOOLS[tool_name]["input_types"]


    # 1. Missing arguments
    for key in schema:
        if key not in args:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required argument: {key}",
            )

    # 2. Extra arguments
    for key in args:
        if key not in schema:
            raise HTTPException(
                status_code=400,
                detail=f"Unexpected argument: {key}",
            )

    # 3. Type checking
    for key, expected_type in schema.items():
        if not isinstance(args[key], expected_type):
            raise HTTPException(
                status_code=400,
                detail=f"Argument '{key}' must be of type {expected_type.__name__}",
            )

def add_numbers(a: int, b: int) -> int:
    return a + b

def subtract_numbers(a: int, b: int) -> int:
    return a - b

def multiply_numbers(a: int, b: int) -> int:
    return a * b
# Older TOOLS 
"""TOOLS = { 
    "add_numbers": {
        "description": "Add two integers",
        "input_schema": {"a": "int", "b": "int"},
        "handler": add_numbers,
    },
    "subtract_numbers": {
        "description": "Subtract b from a",
        "input_schema": {"a": "int", "b": "int"},
        "handler": subtract_numbers,
    },
    "multiply_numbers": {
        "description": "Multiply two integers",
        "input_schema": {"a": "int", "b": "int"},
        "handler": multiply_numbers,
    },
}
"""
TOOLS = {
    "add_numbers": {
        "description": "Add two integers",
        "input_schema": {
            "a": "int",
            "b": "int",
        },
        "input_types": {
            "a": int,
            "b": int,
        },
        "handler": add_numbers,
    },
    "subtract_numbers": {
        "description": "Subtract b from a",
        "input_schema": {
            "a": "int",
            "b": "int",
        },
        "input_types": {
            "a": int,
            "b": int,
        },
        "handler": subtract_numbers,
    },
    "multiply_numbers": {
        "description": "Multiply two integers",
        "input_schema": {
            "a": "int",
            "b": "int",
        },
        "input_types": {
            "a": int,
            "b": int,
        },
        "handler": multiply_numbers,
    },
}

# ------------------
# Request models
# ------------------

class ToolCall(BaseModel):
    tool: str
    args: Dict[str, Any]


# ------------------
# MCP-like endpoints
# ------------------

@app.get("/tools")
def list_tools():
    """
    Tool discovery endpoint (MCP-style).
    """
    return {
        "tools": {
            name: {
                "description": tool["description"],
                "input_schema": tool["input_schema"],
            }
            for name, tool in TOOLS.items()
        }
    }


@app.post("/call")
def call_tool(call: ToolCall, _: None = Depends(require_api_key)):
    if call.tool not in TOOLS:
        raise HTTPException(status_code=404, detail="Unknown tool")

    validate_args(call.tool, call.args)

    try:
        result = TOOLS[call.tool]["handler"](**call.args)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"result": result}
