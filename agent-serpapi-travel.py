# Custom tools || Ref: https://platform.claude.com/docs/en/agent-sdk/custom-tools
# Manual method

import json
import requests
import asyncio
from typing import Any
from claude_agent_sdk import tool, create_sdk_mcp_server, query, ClaudeAgentOptions, AssistantMessage, ResultMessage

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


# Wrap tool in an in-process MCP Server
#  to register it to Claude
flight_search_server = create_sdk_mcp_server(
    name="flight",
    version="1.0",
    tools=[search_flights],
)

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
        hotels = hotels[:5] # limit to top 5 hotels for save tokens; You can adjust this as needed
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

hotel_search_server = create_sdk_mcp_server(
    name="hotel",
    version="1.0",
    tools=[search_hotels],
)


# ========================================================================================================
# ============= Code usage
# ========================================================================================================

SYSTEM_PROMPT = "You're a helpful travel assistant. A user will ask you to find flights and hotels for their trip."
USER_PROMPT = SYSTEM_PROMPT + """
                I have a developer conference in Singapore on April 15, 2026. I'm at Malaysia at the moment. I can spend 5 days there.
                Can you help me with that? 
                If the tool is failed, write in detail what's the issue"""

async def main():
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt=USER_PROMPT,
        options=ClaudeAgentOptions(
            mcp_servers={"flight": flight_search_server, "hotel": hotel_search_server},  # Register the MCP servers with the custom tools
            allowed_tools=["mcp__flight__search_flights", "mcp__hotel__search_hotels"]  # Base: mcp__{server_name}__{tool_name}
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