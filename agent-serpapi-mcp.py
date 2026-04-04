# Try connect SerpApi MCP
# https://platform.claude.com/docs/en/agent-sdk/mcp


import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

# load SerpApi API key from .env file
import os
from dotenv import load_dotenv
load_dotenv()
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")


# Claude Agent with MCP sample code
async def main():
    options = ClaudeAgentOptions(
        mcp_servers={
            "serpapi": {
                "type": "http",
                "url": "https://mcp.serpapi.com/"+ SERPAPI_API_KEY +"/mcp",
            }
        },
        allowed_tools=["mcp__serpapi__*"], #Base name:mcp__<server-name>__<tool-name>
    )

    # USER_PROMPT = "Use the MCP server to explain what it does and how to use it."
    # USER_PROMPT = "Use the MCP server; What's trending news for AI? share links if possible."

    SYSTEM_PROMPT = "Always use the SerpApi MCP server for web search;" # Pro tips add system prompt
    USER_PROMPT = SYSTEM_PROMPT + "Find me a hotel under $100 in Bay Area next week."

    async for message in query(
        prompt=USER_PROMPT,
        options=options,
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


asyncio.run(main())