# AGENTS.MD - LLM Application Development Guide

## Project Overview
This is a Python-based LLM application project focused on developing various LLM interaction patterns including basic LLM calls, multi-turn dialogs, and function/tool calling capabilities. The project uses the OpenAI API with Alibaba Cloud's DashScope service (Qwen models).

## Project Structure
```
llm_app/
├── main.py                 # Entry point with basic hello world
├── llm_call.py             # Basic LLM call implementations (streaming & sync)
├── multi_turn_dialog.py    # Multi-turn conversation implementation
├── function_call.py        # Tool/function calling implementation
├── models.py               # Data models for conversations and messages
├── storage.py              # SQLite-based conversation storage
├── utils.py                # Logging utilities and helper functions
├── prompts.py              # System prompt templates
├── docs/                   # Documentation for various features
│   ├── llm_call.md
│   ├── multi_turn_dialog.md
│   ├── function_call_easy.md
│   ├── function_call_upgrade.md
│   └── workflow.md
├── pyproject.toml          # Project dependencies
└── README.md               # Project roadmap
```

## Dependencies & Setup
- Python 3.11+
- OpenAI Python library (`openai>=2.14.0`)
- Environment variable: `DASHSCOPE_API_KEY` for accessing Alibaba Cloud Qwen models

Install dependencies with:
```bash
uv sync  # or pip install -r requirements.txt if using pip
```

## Key Commands
- **Run main application**: `python main.py`
- **Test LLM calls**: `python llm_call.py`
- **Test function calls**: `python function_call.py`
- **Start multi-turn dialog**: `python multi_turn_dialog.py`
- **Run tests**: `python -m pytest` (if tests exist)

## Code Architecture

### Core Components
1. **Conversation Management** (`models.py`):
   - `Conversation` class handles message history and storage
   - Role enum: SYSTEM, USER, ASSISTANT, TOOL
   - Type enum: TEXT, FUNCTION, TOOL_RESULT

2. **Storage Layer** (`storage.py`):
   - SQLite database for persisting conversations
   - `ConversationStorage` class with CRUD operations for conversations and messages

3. **LLM Interaction** (`llm_call.py`):
   - Streaming and synchronous LLM calls
   - Integration with DashScope/Qwen API
   - Comprehensive logging of interactions

4. **Tool Calling** (`function_call.py`):
   - Support for function/tool calling with LLM
   - Tool definition and execution framework
   - Recursive tool calling capability

### Message Flow Pattern
- System message → User message → Assistant response (may include tool calls) → Tool results → Final response
- Messages are stored with role, content, and type information
- Tool calls are serialized and deserialized properly

## Conventions & Patterns

### Logging
- JSON-formatted logging to both console and file (`llm_calls.log`)
- Structured logging with fields: event, message, response_text, elapsed_time, token usage
- Separate logging for LLM calls and tool calls

### Error Handling
- API key validation before making calls
- Graceful handling of missing responses
- Token usage validation to prevent errors

### Configuration
- API keys loaded from environment variables (`DASHSCOPE_API_KEY`)
- Model selection: `qwen-plus` for streaming, `qwen-flash` for regular calls
- Temperature settings for controlling creativity (default 1.0)

## Gotchas & Important Notes

1. **Environment Variables**: The application requires `DASHSCOPE_API_KEY` to be set in the environment
2. **Token Usage**: Monitor token usage as it's logged but not actively managed for cost control
3. **Database Initialization**: SQLite database is created automatically on first use
4. **Tool Call Limitations**: The example tools use mock implementations (random weather/temp)
5. **Chinese Language**: System prompts and some comments are in Chinese
6. **Type Hints**: Extensive use of type hints, especially for OpenAI API objects

## Testing Approach
- The project includes a `flush_test.py` file for testing purposes
- Manual testing through CLI interfaces for each major feature
- Stream and synchronous LLM call testing

## Development Workflow
1. Set up environment variables
2. Implement new features in separate modules
3. Test through CLI interfaces
4. Check logs for debugging and performance metrics
5. Persist conversations using the storage layer