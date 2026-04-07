import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, UserMessage, SystemMessage
from claude_agent_sdk.types import TextBlock, ToolUseBlock, ToolResultBlock, ThinkingBlock

# Load SERPAPI_API_KEY for claude skill
import os
from dotenv import load_dotenv
load_dotenv()
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

async def main():
    options = ClaudeAgentOptions(
        cwd=".claude/skills/serpapi-basic-skill",  # Project with .claude/skills/
        setting_sources=["user", "project"],  # Load Skills from filesystem
        allowed_tools=["Skill", "Read", "Write", "Bash"],  # Enable Skill tool
    )

    # USER_PROMPT = "What is your serpapi skill?
    USER_PROMPT = "Use the SerpApi skill. What is trending topic in healthcare now? share link for reference"
    async for message in query(
        prompt=USER_PROMPT, options=options
    ):
        print("\n" + "="*50)
        print("\n  Received message:")

        print(f"\n[MSG TYPE]: {type(message).__name__}")

        if isinstance(message, AssistantMessage):
            print(f"  Model: {message.model}")
            for block in message.content:
                print("  ---")
                if isinstance(block, TextBlock):
                    print(f"  TextBlock: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"  ToolUseBlock: {block.name}({block.input})")
                elif isinstance(block, ToolResultBlock):
                    print(f"  ToolResultBlock: {block.content}")
                elif isinstance(block, ThinkingBlock):
                    print(f"  ThinkingBlock: {block.thinking[:80]}...")
                else:
                    print(f"  Unknown block: {block}")

        elif isinstance(message, UserMessage):
            print(f"  UserMessage: {str(message.content)[:100]}")

        elif isinstance(message, SystemMessage):
            print(f"  SystemMessage subtype: {message.subtype}")
            # These are internal SDK events — usually safe to ignore

        elif isinstance(message, ResultMessage):
            print(f"  ResultMessage: subtype={message.subtype}")
            print(f"  Result text: {message.result}")
            print(f"  Cost: ${message.total_cost_usd}")
            print(f"  Turns: {message.num_turns}")

asyncio.run(main())