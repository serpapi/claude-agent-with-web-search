import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


#PROMPT = "What's trending news in Indonesia at the moment?. Share article link for each"
PROMPT = "Share flight info from Jakarta to Bali on April 5th? Share price in IDR, time detail, flight number, and resource for each. Don't hallucinate"  

async def main():
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt=PROMPT,
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