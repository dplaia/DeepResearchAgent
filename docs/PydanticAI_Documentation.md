# PydanticAI Cheat Sheet for LLMs (Part 1)

**PydanticAI: Build Production-Grade Generative AI Apps in Python**

*   Python Agent Framework for building robust GenAI applications.
*   Inspired by FastAPI's ergonomic design.
*   Leverages Pydantic for data validation and structure.
*   Model-agnostic: Supports OpenAI, Anthropic, Gemini, Ollama, Groq, Mistral, and more.
*   Key Features:
    *   Type-safe agents with Pydantic.
    *   Structured responses.
    *   Dependency Injection for testing and modularity.
    *   Streaming LLM outputs.
    *   Integration with Pydantic Logfire for observability.

---

**1. Agents: The Core Building Block**

*   Agents are containers for interacting with LLMs.
*   Think of them as similar to FastAPI apps or API Routers - instantiate once and reuse.
*   Key components of an Agent:
    *   `system_prompt`: Instructions for the LLM (static or dynamic).
    *   `tools`: Functions the LLM can call to get information (optional).
    *   `result_type`: Pydantic model to structure LLM output (optional).
    *   `deps_type`: Pydantic dataclass defining dependencies (optional).
    *   `model`: LLM model to use (e.g., 'openai:gpt-4o').
    *   `model_settings`: Fine-tune model behavior (temperature, etc.).

**Example: Simple Agent**

```python
from pydantic_ai import Agent

agent = Agent(
    'gemini-1.5-flash',
    system_prompt='Be concise, reply with one sentence.',
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.data)

2. Running Agents: run(), run_sync(), run_stream()
    • agent.run(user_prompt, **kwargs):
        ◦ Asynchronous method.
        ◦ Returns a RunResult object containing the completed response.
    • agent.run_sync(user_prompt, **kwargs):
        ◦ Synchronous method.
        ◦ Returns a RunResult object.
        ◦ Wraps agent.run() internally.
    • agent.run_stream(user_prompt, **kwargs):
        ◦ Asynchronous method for streaming responses.
        ◦ Returns a StreamedRunResult object, which is an async context manager.
        ◦ Use async with agent.run_stream(...) as result: to access stream.
Example: Running Agents
from pydantic_ai import Agent
import asyncio

agent = Agent('openai:gpt-4o')

# Synchronous run
result_sync = agent.run_sync('What is the capital of Italy?')
print(result_sync.data)

# Asynchronous run
async def main():
    result_async = await agent.run('What is the capital of France?')
    print(result_async.data)

    async with agent.run_stream('What is the capital of the UK?') as response_stream:
        async for message in response_stream.stream_text():
            print(message, end="") # Stream text chunks

asyncio.run(main())

3. System Prompts: Guiding the LLM
    • Instructions for the LLM, defined in system_prompt argument of Agent.
    • Static System Prompts: Defined as strings directly in Agent initialization.
    • Dynamic System Prompts: Defined as functions decorated with @agent.system_prompt.
        ◦ Dynamic prompts can access RunContext and dependencies.
        ◦ Can be async or sync functions.
        ◦ Multiple system prompts are appended in the order they are defined.
Example: Static and Dynamic System Prompts
from pydantic_ai import Agent, RunContext
from datetime import date

agent = Agent(
    'openai:gpt-4o',
    deps_type=str,
    system_prompt="Use the customer's name while replying to them.", # Static prompt
)

@agent.system_prompt # Dynamic prompt
def add_the_users_name(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps}."

@agent.system_prompt # Another dynamic prompt
def add_the_date() -> str:
    return f'The date is {date.today()}.'

result = agent.run_sync('What is the date?', deps='Frank')
print(result.data)

4. Tools (Function Tools): Extending Agent Capabilities
    • Functions that Agents can use to get extra information during a run.
    • Registered using decorators:
        ◦ @agent.tool: Tools that need access to RunContext.
        ◦ @agent.tool_plain: Tools that DO NOT need RunContext.
    • Can also be registered using the tools argument in Agent initialization.
    • Tools can be sync or async functions.
    • Function parameters are automatically extracted to define tool schema.
    • Docstrings are used for tool and parameter descriptions (supports Google, Numpy, Sphinx formats).
Example: Tool Registration and Usage
from pydantic_ai import Agent, RunContext
import random

agent = Agent(
    'gemini-1.5-flash',
    deps_type=str,
    system_prompt=(
        "You're a dice game, you should roll the die and see if the number "
        "matches the user's guess. If so, tell them they're a winner."
    ),
)

@agent.tool_plain # Tool without RunContext
def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))

@agent.tool # Tool with RunContext
def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name."""
    return ctx.deps

dice_result = agent.run_sync('My guess is 4', deps='Anne')
print(dice_result.data)

5. Dependency Injection: Providing Context to Agents
    • Provides data and services to agents, system prompts, tools, and result validators.
    • Use deps_type in Agent to define the dependency class (typically a Pydantic dataclass).
    • Dependencies are accessed via ctx.deps within RunContext in system prompts and tools.
    • Useful for testing and iterative development.
    • override() method on Agent for replacing dependencies during testing.
Example: Dependency Injection

from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
import httpx

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent(
    'openai:gpt-4o',
    deps_type=MyDeps,
)

@agent.system_prompt
async def get_system_prompt(ctx: RunContext[MyDeps]) -> str:
    response = await ctx.deps.http_client.get(
        'https://example.com',
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
    )
    response.raise_for_status()
    return f'Prompt: {response.text}'

async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run('Hello', deps=deps)
        print(result.data)

asyncio.run(main())
    


# PydanticAI Cheat Sheet for LLMs (Part 2)

---

**6. Models: Choosing and Configuring LLMs**

*   PydanticAI is model-agnostic, supporting various providers.
*   **Supported Providers:** OpenAI, Anthropic, Gemini (Generative Language API & VertexAI API), Ollama, Groq, Mistral.
*   **Model Specification:**  Use model names as strings in `Agent` initialization (e.g., `'openai:gpt-4o'`, `'anthropic:claude-3-5-sonnet-latest'`).
*   **API Keys:**
    *   Environment variables: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`.
    *   `api_key` argument in `Model` class initialization.
    *   Platform-specific authentication (e.g., Google Cloud Platform for VertexAI).
*   **Model Settings:**
    *   Control model behavior using `model_settings` argument in `Agent` or `run()` methods.
    *   `ModelSettings` class (or provider-specific subclasses like `AnthropicModelSettings`).
    *   Common settings: `temperature`, `max_tokens`, `timeout`, `top_p`, `presence_penalty`, `frequency_penalty`, `logit_bias`.

**Example: Specifying and Configuring Models**

```python
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings

# Agent with default model (openai:gpt-4o)
agent_default = Agent()

# Agent with specific model and settings
agent_configured = Agent(
    'anthropic:claude-3-5-sonnet-latest',
    model_settings=ModelSettings(temperature=0.7, max_tokens=200)
)

# Run with runtime model settings override
result = agent_default.run_sync(
    'Explain quantum physics.',
    model_settings={'temperature': 0.2} # Override temperature for this run
)
print(result.data)


7. Results: Accessing and Validating LLM Outputs
    • Agent run(), run_sync(), and run_stream() methods return result objects (RunResult and StreamedRunResult).
    • RunResult: For non-streamed runs.
        ◦ result.data: Access the validated result data (based on result_type).
        ◦ result.usage(): Get usage statistics (tokens, requests).
        ◦ result.all_messages(): Get all messages in the run history.
        ◦ result.new_messages(): Get messages from the current run only.
    • StreamedRunResult: For streamed runs.
        ◦ Async context manager (async with ...:).
        ◦ result.stream(): Async iterator for structured data chunks.
        ◦ result.stream_text(): Async iterator for text chunks.
        ◦ result.stream_structured(debounce_by=0.01): Async iterator for debounced structured data chunks with partial validation.
        ◦ result.get_data(): Await to get the full, validated result data after the stream completes.
        ◦ Usage and message access methods similar to RunResult (available after stream completion).
    • Result Validators: Functions decorated with @agent.result_validator to perform custom validation after model response.
        ◦ Can raise ModelRetry to request the model to retry.
        ◦ Can access RunContext and dependencies.
Example: Result Validation and Access
from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic import BaseModel, Field

class SentimentResult(BaseModel):
    sentiment: str = Field(description="Sentiment of the text (positive, negative, neutral)")

agent = Agent(result_type=SentimentResult)

@agent.result_validator
async def validate_sentiment(ctx: RunContext, result: SentimentResult) -> SentimentResult:
    if result.sentiment not in ['positive', 'negative', 'neutral']:
        raise ModelRetry("Sentiment must be 'positive', 'negative', or 'neutral'")
    return result

result = agent.run_sync("The movie was amazing!")
print(result.data)
print(result.usage())


8. Testing and Evals: Ensuring Quality
    • Unit Tests: Test application code logic, use testing models to avoid LLM calls.
        ◦ Use pytest and anyio for async testing.
        ◦ TestModel: Mock LLM, returns dummy data, calls tools.
        ◦ FunctionModel: More control over model behavior in tests, define custom functions to simulate model responses.
        ◦ Agent.override(model=...): Replace agent's model for testing context.
        ◦ ALLOW_MODEL_REQUESTS=False: Global setting to prevent accidental real LLM requests in tests.
        ◦ capture_run_messages(): Context manager to inspect messages exchanged during a run.
    • Evals: Evaluate LLM performance, more like benchmarks, track changes over time.
        ◦ End-to-end tests: Test final output (e.g., SQL generation).
        ◦ Synthetic self-contained tests: Unit-test style checks on model responses.
        ◦ LLM-based evals: Use another LLM to evaluate the agent's output.
        ◦ Evals in prod: Measure real-world performance in production.
Example: Unit Testing with TestModel
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
import pytest
import asyncio

agent = Agent()

async def test_agent_behavior():
    with agent.override(model=TestModel()): # Override model with TestModel
        result = await agent.run("Hello")
        assert isinstance(result.data, str) # Dummy text response

asyncio.run(test_agent_behavior())
    

9. Pydantic Logfire: Observability and Monitoring
    • Integration with Pydantic Logfire for real-time debugging, performance monitoring, and behavior tracking.
    • Commercial product, free tier available.
    • Install pydantic-ai[logfire] and logfire-api.
    • Configure Logfire: logfire.configure().
    • Instrument asyncpg: logfire.instrument_asyncpg().
    • Use Logfire UI (live view, SQL, dashboards) to observe agent behavior.
    • No overhead if logfire package is not installed.
Example: Enabling Logfire
from pydantic_ai import Agent
import logfire
from bank_database import DatabaseConn # Assuming bank_database is defined

logfire.configure() # Configure Logfire

agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDependencies, # Assuming SupportDependencies is defined
    result_type=SupportResult, # Assuming SupportResult is defined
    # ... system_prompt and tools ...
)

# ... rest of the agent code ...


10. Multi-Agent Applications: Complex Workflows
    • Agent Delegation: One agent calls another agent as a tool.
        ◦ Delegate agent typically shares or has a subset of the calling agent's dependencies.
        ◦ Use ctx.usage to pass usage information to delegate agents.
        ◦ Can use different models for different agents in delegation.
    • Programmatic Agent Hand-off: Application code or human user decides which agent to call next in a sequence.
        ◦ Agents don't need to share dependencies.
    • Graph-Based Control Flow: For very complex applications, use a graph-based state machine to manage multiple agents.
Example: Agent Delegation
from pydantic_ai import Agent, RunContext, UsageLimits

joke_selection_agent = Agent(
    'openai:gpt-4o',
    system_prompt=(
        'Use the `joke_factory` to generate some jokes, then choose the best. '
        'You must return just a single joke.'
    ),
)

joke_generation_agent = Agent('gemini-1.5-flash', result_type=list[str])

@joke_selection_agent.tool
async def joke_factory(ctx: RunContext[None], count: int) -> list[str]:
    r = await joke_generation_agent.run(
        f'Please generate {count} jokes.',
        usage=ctx.usage,
    )
    return r.data

result = joke_selection_agent.run_sync(
    'Tell me a joke.',
    usage_limits=UsageLimits(request_limit=5, total_tokens_limit=300),
)
print(result.data)
    

This completes the two-part cheat sheet for PydanticAI. This should provide LLMs with a good overview of the library's key features and concepts. Let me know if you'd like any adjustments or further sections!




