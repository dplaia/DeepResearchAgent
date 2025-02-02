[Skip to content](https://ai.pydantic.dev/install/#installation)

# Installation

PydanticAI is available on PyPI as [`pydantic-ai`](https://pypi.org/project/pydantic-ai/) so installation is as simple as:

[pip](https://ai.pydantic.dev/install/#__tabbed_1_1)[uv](https://ai.pydantic.dev/install/#__tabbed_1_2)

```
pip install pydantic-ai

```

```
uv add pydantic-ai

```

(Requires Python 3.9+)

This installs the `pydantic_ai` package, core dependencies, and libraries required to use all the models
included in PydanticAI. If you want to use a specific model, you can install the ["slim"](https://ai.pydantic.dev/install/#slim-install) version of PydanticAI.

## Use with Pydantic Logfire

PydanticAI has an excellent (but completely optional) integration with [Pydantic Logfire](https://pydantic.dev/logfire) to help you view and understand agent runs.

To use Logfire with PydanticAI, install `pydantic-ai` or `pydantic-ai-slim` with the `logfire` optional group:

[pip](https://ai.pydantic.dev/install/#__tabbed_2_1)[uv](https://ai.pydantic.dev/install/#__tabbed_2_2)

```
pip install 'pydantic-ai[logfire]'

```

```
uv add 'pydantic-ai[logfire]'

```

From there, follow the [Logfire setup docs](https://ai.pydantic.dev/logfire/#using-logfire) to configure Logfire.

## Running Examples

We distribute the [`pydantic_ai_examples`](https://github.com/pydantic/pydantic-ai/tree/main/pydantic_ai_examples) directory as a separate PyPI package ( [`pydantic-ai-examples`](https://pypi.org/project/pydantic-ai-examples/)) to make examples extremely easy to customize and run.

To install examples, use the `examples` optional group:

[pip](https://ai.pydantic.dev/install/#__tabbed_3_1)[uv](https://ai.pydantic.dev/install/#__tabbed_3_2)

```
pip install 'pydantic-ai[examples]'

```

```
uv add 'pydantic-ai[examples]'

```

To run the examples, follow instructions in the [examples docs](https://ai.pydantic.dev/examples/).

## Slim Install

If you know which model you're going to use and want to avoid installing superfluous packages, you can use the [`pydantic-ai-slim`](https://pypi.org/project/pydantic-ai-slim/) package.
For example, if you're using just [`OpenAIModel`](https://ai.pydantic.dev/api/models/openai/#pydantic_ai.models.openai.OpenAIModel), you would run:

[pip](https://ai.pydantic.dev/install/#__tabbed_4_1)[uv](https://ai.pydantic.dev/install/#__tabbed_4_2)

```
pip install 'pydantic-ai-slim[openai]'

```

```
uv add 'pydantic-ai-slim[openai]'

```

`pydantic-ai-slim` has the following optional groups:

- `logfire` — installs [`logfire`](https://ai.pydantic.dev/logfire/) [PyPI ↗](https://pypi.org/project/logfire)
- `graph` \- installs [`pydantic-graph`](https://ai.pydantic.dev/graph/) [PyPI ↗](https://pypi.org/project/pydantic-graph)
- `openai` — installs `openai` [PyPI ↗](https://pypi.org/project/openai)
- `vertexai` — installs `google-auth` [PyPI ↗](https://pypi.org/project/google-auth) and `requests` [PyPI ↗](https://pypi.org/project/requests)
- `anthropic` — installs `anthropic` [PyPI ↗](https://pypi.org/project/anthropic)
- `groq` — installs `groq` [PyPI ↗](https://pypi.org/project/groq)
- `mistral` — installs `mistralai` [PyPI ↗](https://pypi.org/project/mistralai)

See the [models](https://ai.pydantic.dev/models/) documentation for information on which optional dependencies are required for each model.

You can also install dependencies for multiple models and use cases, for example:

[pip](https://ai.pydantic.dev/install/#__tabbed_5_1)[uv](https://ai.pydantic.dev/install/#__tabbed_5_2)

```
pip install 'pydantic-ai-slim[openai,vertexai,logfire]'

```

```
uv add 'pydantic-ai-slim[openai,vertexai,logfire]'

```