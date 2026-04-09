# Custom tools || Ref: https://platform.claude.com/docs/en/agent-sdk/custom-tools
# Manual method

import time
import json
import requests
import asyncio
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server, query, ClaudeAgentOptions, AssistantMessage, ResultMessage
from claude_agent_sdk.types import StreamEvent

import os
from dotenv import load_dotenv
load_dotenv()
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")


# ========================================================================================================
# ============= Custom Tool preparation
# ============= Google Flights API
# ========================================================================================================
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
        flight_type = args.get("type", 1)  # Default to round trip if not provided
        outbound_date = args["outbound_date"]
        return_date = args.get("return_date", "")

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
        flights = results.get("best_flights", [])[:2] #optional: other_flights #:2 to limit to top 2 flights for save tokens; You can adjust this as needed
        if not flights:
            return "No flights found."
        
        print("--- Successfully fetched flight data")  # Debugging statement

        # Return a content array - Claude sees this as the tool result
        #   supported type: text, image, resource
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


# ========================================================================================================
# ============= Custom Tool preparation
# ============= Google Hotels API
# ========================================================================================================

# Google Hotels API need check_in_date, check_out_date, and "q". as search query, option: min_price, max_price

@tool(
    name="search_hotels",
    description="Search for hotels using SerpApi. Input should be a JSON string with 'q', 'check_in_date', and 'check_out_date' fields.",
    input_schema={
        "type": "object",
        "properties": {
            "q": {"type": "string", "description": "Search query, e.g., 'hotels in Singapore'"},
            "check_in_date": {"type": "string", "description": "Check-in date in YYYY-MM-DD format"},
            "check_out_date": {"type": "string", "description": "Check-out date in YYYY-MM-DD format"},
            "min_price": {"type": "number", "description": "Minimum price filter (optional)"},
            "max_price": {"type": "number", "description": "Maximum price filter (optional)"},
        },
        "required": ["q", "check_in_date", "check_out_date"],
    },
)
async def search_hotels(args: dict[str, Any]) -> dict[str, Any]:
    print("---Received search_hotels tool call with args:", args)  # Debugging statement
    try:
        q = args["q"]
        check_in_date = args["check_in_date"]
        check_out_date = args["check_out_date"]
        min_price = args.get("min_price")
        max_price = args.get("max_price")

        print(f"Parsed input - Query: {q}, Check-in: {check_in_date}, Check-out: {check_out_date}, Min Price: {min_price}, Max Price: {max_price}")  # Debugging statement

    except (json.JSONDecodeError, KeyError) as e:
        return f"Invalid input: {e}"

    # Call SerpApi Google Hotels Search
    params = {
        "engine": "google_hotels",
        "api_key": SERPAPI_API_KEY,
        "q": q,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
    }

    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price

    response = requests.get("https://serpapi.com/search", params=params)

    if response.status_code == 200:
        results = response.json()
        hotels = results.get("properties", [])
        hotels = hotels[:2] # limit to top 2 hotels for save tokens; You can adjust this as needed
        if not hotels:
            return "No hotels found."
        
        print("--- Successfully fetched hotel data")  # Debugging statement

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(hotels, indent=2)  
                }
            ]
        }
    else:
        print("--- Error fetching hotel data:", response.status_code, response.text)  # Debugging statement
        return f"Error fetching hotel data: {response.status_code}"


# ========================================================================================================
# ============= Wrap tool in an in-process MCP Server
# ========================================================================================================
travel_search_server = create_sdk_mcp_server(
    name="travel",
    version="1.0",
    tools=[search_flights, search_hotels],  # You can register multiple tools under the same server
)


# ========================================================================================================
# ============= Code usage
# ========================================================================================================

SYSTEM_PROMPT = """You're a helpful travel assistant. Help user for their trip.
- Search flights using the `search_flights` tool
- Search hotels using the `search_hotels` tool
- Combine the results to find the best options for the user based on their preferences and constraints.
- If you encounter any issues with the tools, explain the problem in detail."""

# Simple sample
USER_PROMPT = """ I have a developer conference in Singapore on April 30, 2026. I'm at Malaysia at the moment. I can spend 5 days there.
                Can you help me with that?"""

# More complex sample
# USER_PROMPT = """ Need to fly to Singapore on May 1st, 2026. Spend a day there, 
#                 then go to Jakarta for 2 days, before back to Malaysia.
#                 Total budget is around $1000."""


async def main():
    start_time = time.perf_counter()

    async for message in query(
        prompt=USER_PROMPT,
        options=ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            include_partial_messages=True,
            mcp_servers={"travel": travel_search_server},  # Register the MCP servers with the custom tools
            allowed_tools=["mcp__travel__search_flights", "mcp__travel__search_hotels"],  # Base: mcp__{server_name}__{tool_name}
            disallowed_tools=["Read"]
        ),
    ):
        # Print human-readable output
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print("\nClaude Reasoning:", end=" ")
                    print(block.text)  # Claude's reasoning
                elif hasattr(block, "name"):
                    print(f"\nTool: {block.name}")  # Tool being called
        elif isinstance(message, ResultMessage):
            print(f"\nDone: {message.subtype}")  # Final result

        # Optional: to stream event
        # if isinstance(message, StreamEvent):
        #     event = message.event
        #     if event.get("type") == "content_block_delta":
        #         delta = event.get("delta", {})
        #         if delta.get("type") == "text_delta":
        #             print(delta.get("text", ""), end="", flush=True)

    # Log time
    elapsed = time.perf_counter() - start_time
    print(f"Elapsed time: {elapsed:.2f} seconds")

asyncio.run(main())