import requests
import json
from ollama import chat

MCP_BASE_URL = "http://127.0.0.1:8000"
API_KEY = "supersecretkey"
MODEL = "qwen3:1.7b"


def get_tools():
    resp = requests.get(f"{MCP_BASE_URL}/tools")
    resp.raise_for_status()
    return resp.json()["tools"]

def reflect_and_retry(
    tools: dict,
    user_request: str,
    prev_tool_call: dict,
    error_message: str,
) -> dict:
    system_prompt = (
        "You are an agent correcting a failed tool call.\n"
        "You previously attempted a tool call that failed.\n"
        "Fix the mistake and output ONLY valid JSON with keys: tool, args."
    )

    user_prompt = (
        f"Available tools:\n{json.dumps(tools, indent=2)}\n\n"
        f"User request: {user_request}\n\n"
        f"Previous tool call:\n{json.dumps(prev_tool_call, indent=2)}\n\n"
        f"Error message:\n{error_message}\n\n"
        "Return a corrected tool call as JSON only."
    )

    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0.0},
    )

    return json.loads(response.message.content)

def decide_tool(tools: dict, user_request: str) -> dict:
    system_prompt = (
    "You are an agent that selects the correct tool.\n"
    "You MUST choose exactly one tool from the list.\n"
    "Use the tool description to decide.\n"
    "Pay attention to verbs like add, subtract, multiply.\n"
    "Output ONLY valid JSON with keys: tool, args."
)

    user_prompt = (
        f"Available tools:\n{json.dumps(tools, indent=2)}\n\n"
        f"User request: {user_request}\n\n"
        "Respond with JSON only."
    )

    response = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={"temperature": 0.0},
    )

    return json.loads(response.message.content)


def call_tool(tool_call: dict):
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
    }

    resp = requests.post(
        f"{MCP_BASE_URL}/call",
        headers=headers,
        json=tool_call,
    )
    resp.raise_for_status()
    return resp.json()

def safe_call_tool(tool_call: dict) -> tuple[bool, str | dict]:
    try:
        result = call_tool(tool_call)
        return True, result
    except Exception as e:
        return False, str(e)

def run_agent(user_request: str, max_retries: int = 2):
    tools = get_tools()

    tool_call = decide_tool(tools, user_request)

    for attempt in range(max_retries + 1):
        print(f"\nAttempt {attempt + 1}")
        print("Tool call:", tool_call)

        success, result_or_error = safe_call_tool(tool_call)

        if success:
            return result_or_error

        print("Tool failed with error:", result_or_error)

        if attempt == max_retries:
            raise RuntimeError("Agent failed after retries")

        tool_call = reflect_and_retry(
            tools,
            user_request,
            tool_call,
            result_or_error,
        )



if __name__ == "__main__":
    tests = [
        "Add 3 and 4",
        "Subtract 10 from 3",
        "Multiply 6 by 7",
        "What is 8 times 5?",
    ]

    for t in tests:
        print("\nUser:", t)
        print("Agent result:", run_agent(t))
