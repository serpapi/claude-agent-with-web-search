# Custom tools || Ref: https://platform.claude.com/docs/en/agent-sdk/custom-tools
# Manual method

import time
import json
import requests
import asyncio
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server, query, ClaudeAgentOptions, AssistantMessage, ResultMessage

import os
from dotenv import load_dotenv
load_dotenv()
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

# Custom tool: SerpApi Google Flights Search
@tool(
    name="search_flights",
    description="Search for flights using SerpApi. Input should be a JSON string with 'origin', 'destination', and 'date' fields.",
    input_schema={
        "type": "object",
        "properties": {
            "departure_id": {"type": "string", "description": "IATA code of the departure airport"},
            "arrival_id": {"type": "string", "description": "IATA code of the arrival airport"},            
            "type": {"type": "number", "description": "Type of flight search: 1 for round trip (default), 2 for one way"},
            "outbound_date": {"type": "string", "description": "Departure date in YYYY-MM-DD format"},
            "return_date": {"type": "string", "description": "Return date in YYYY-MM-DD format (required if type is 1)"},
        },
        "required": ["departure_id", "arrival_id", "type", "outbound_date"],
    },
)
async def search_flights(args: dict[str, Any]) -> dict[str, Any]:
    print("---Received search_flights tool call with args:", args)  # Debugging statement
    try:
        departure_id = args["departure_id"]
        arrival_id = args["arrival_id"]
        flight_type = args["type"]  #args.get("type", 1)  # Default to round trip if not provided
        outbound_date = args["outbound_date"]
        return_date = args["return_date"] #args.get("return_date", "")

        print(f"Parsed input - Departure: {departure_id}, Arrival: {arrival_id}, Type: {flight_type}, Outbound Date: {outbound_date}, Return Date: {return_date}")  # Debugging statement

    except (json.JSONDecodeError, KeyError) as e:
        return f"Invalid input: {e}"

    # Call SerpApi Google Flights Search
    params = {
        "engine": "google_flights",
        "api_key": SERPAPI_API_KEY,
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "type": flight_type,
        "outbound_date": outbound_date,
    }

    if flight_type == 1 and return_date:
        params["return_date"] = return_date

    response = requests.get("https://serpapi.com/search", params=params)

    if response.status_code == 200:
        results = response.json()
        # Extract relevant flight information (this is just an example, adjust as needed)
        flights = results.get("best_flights", []) #optional: other_flights
        if not flights:
            return "No flights found."
        
        print("--- Successfully fetched flight data")  # Debugging statement

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(flights, indent=2)  
                }
            ]
        }
    else:
        print("--- Error fetching flight data:", response.status_code, response.text)  # Debugging statement
        return f"Error fetching flight data: {response.status_code}"


# Wrap tool in an in-process MCP Server
#  to register it to Claude
flight_search_server = create_sdk_mcp_server(
    name="flight",
    version="1.0",
    tools=[search_flights],
)

USER_PROMPT = "I want to find a flight from Jakarta to Singapore departing on 2026-04-20 and returning on 2026-04-27. Can you help me with that? If the tool is failed, write in detail what's the issue"

async def main():
    start_time = time.perf_counter()
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt=USER_PROMPT,
        options=ClaudeAgentOptions(
            mcp_servers={"flight": flight_search_server},  # Register the MCP server with the custom tool
            allowed_tools=["mcp__flight__search_flights"]  # Base: mcp__{server_name}__{tool_name}
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

    
    # Log time
    elapsed = time.perf_counter() - start_time
    print(f"Elapsed time: {elapsed:.2f} seconds")


asyncio.run(main())