# About
A sample usage of Claude Agent SDK with SerpApi. See how to connect your AI agent to live web search results.

- [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview): An SDK provided by Anthropic team to create agent programmatically
- [SerpApi](https://serpapi.com/use-cases/ai-search-engine-api): A simple API to access search engine results that you can use either for any application or specifically for AI/LLM.

## Run locally

Create env setup (one time only):
```
python3 -m venv path/to/venv
```

Activate the env
```
source path/to/venv/bin/activate
```

Run the code
```
python $filename.py
```

## File Information
- Agent File (for testing only) - `agent-basic-file.py`
- Native web search - `agent-native-websearch.py` # Not optimal result
- Custom tool (SerpApi - one tool) - `agent-serpapi-flight.py`
- Custom tool (SerpApi - multiple tools) - `agent-serpapi-travel.py`
- Connect MCP  - Server SerpApi  - `agent-serpapi-mcp.py`
- Connect Claude skills - SerpApi - `agent-serpapi-skill.py`

## Resources

- Blog post: [Claude Agent SDK tutorial](serpapi.com/blog/build-an-ai-agent-with-claude-agent-sdk/)
- Video tutorial (coming soon..)