# Try connect SerpApi MCP
# https://platform.claude.com/docs/en/agent-sdk/mcp


import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

# Custom tool: SerpApi Google Flights Search
@tool(
    name="Flight search",
    description="Search for flights using SerpApi. Input should be a JSON string with 'origin', 'destination', and 'date' fields.",
    input_schema={
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "IATA code of the departure airport"},
            "destination": {"type": "string", "description": "IATA code of the arrival airport"},
            "date": {"type": "string", "description": "Date of the flight in YYYY-MM-DD format"},
        },
        "required": ["origin", "destination", "date"],
    },
)


async def main():
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt="What's trending news in Indonesia at the moment?",
        options=ClaudeAgentOptions(
            allowed_tools=["WebSearch"],  # Tools Claude can use
        ),
    ):
        # Print human-readable output
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print("Claude Reasoning:", end=" ")
                    print(block.text)  # Claude's reasoning
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")  # Tool being called
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")  # Final result


asyncio.run(main())