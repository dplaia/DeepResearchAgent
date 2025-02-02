[Skip to content](https://ai.pydantic.dev/models/#openai)

Version Notice


This documentation is ahead of the last release by
[13 commits](https://github.com/pydantic/pydantic-ai/compare/v0.0.20...main).
You may see documentation for features not yet supported in the latest release [v0.0.20 2025-01-23](https://github.com/pydantic/pydantic-ai/releases/tag/v0.0.20).


# Models

PydanticAI is Model-agnostic and has built in support for the following model providers:

- [OpenAI](https://ai.pydantic.dev/models/#openai)
- [Anthropic](https://ai.pydantic.dev/models/#anthropic)
- Gemini via two different APIs: [Generative Language API](https://ai.pydantic.dev/models/#gemini) and [VertexAI API](https://ai.pydantic.dev/models/#gemini-via-vertexai)
- [Ollama](https://ai.pydantic.dev/models/#ollama)
- [Groq](https://ai.pydantic.dev/models/#groq)
- [Mistral](https://ai.pydantic.dev/models/#mistral)

See [OpenAI-compatible models](https://ai.pydantic.dev/models/#openai-compatible-models) for more examples on how to use models such as [OpenRouter](https://ai.pydantic.dev/models/#openrouter), [Grok (xAI)](https://ai.pydantic.dev/models/#grok-xai) and [DeepSeek](https://ai.pydantic.dev/models/#deepseek) that support the OpenAI SDK.

You can also [add support for other models](https://ai.pydantic.dev/models/#implementing-custom-models).

PydanticAI also comes with [`TestModel`](https://ai.pydantic.dev/api/models/test/) and [`FunctionModel`](https://ai.pydantic.dev/api/models/function/) for testing and development.

To use each model provider, you need to configure your local environment and make sure you have the right packages installed.

## OpenAI

### Install

To use OpenAI models, you need to either install [`pydantic-ai`](https://ai.pydantic.dev/install/), or install [`pydantic-ai-slim`](https://ai.pydantic.dev/install/#slim-install) with the `openai` optional group:

[pip](https://ai.pydantic.dev/models/#__tabbed_1_1)[uv](https://ai.pydantic.dev/models/#__tabbed_1_2)

```
pip install 'pydantic-ai-slim[openai]'

```

```
uv add 'pydantic-ai-slim[openai]'

```

### Configuration

To use [`OpenAIModel`](https://ai.pydantic.dev/api/models/openai/#pydantic_ai.models.openai.OpenAIModel) through their main API, go to [platform.openai.com](https://platform.openai.com/) and follow your nose until you find the place to generate an API key.

### Environment variable

Once you have the API key, you can set it as an environment variable:

```
export OPENAI_API_KEY='your-api-key'

```

You can then use [`OpenAIModel`](https://ai.pydantic.dev/api/models/openai/#pydantic_ai.models.openai.OpenAIModel) by name:

openai\_model\_by\_name.py

```
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o')
...

```

Or initialise the model directly with just the model name:

openai\_model\_init.py

```
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel('gpt-4o')
agent = Agent(model)
...

```

### `api_key` argument

If you don't want to or can't set the environment variable, you can pass it at runtime via the [`api_key` argument](https://ai.pydantic.dev/api/models/openai/#pydantic_ai.models.openai.OpenAIModel.__init__):

openai\_model\_api\_key.py

```
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel('gpt-4o', api_key='your-api-key')
agent = Agent(model)
...

```

### Custom OpenAI Client

`OpenAIModel` also accepts a custom `AsyncOpenAI` client via the [`openai_client` parameter](https://ai.pydantic.dev/api/models/openai/#pydantic_ai.models.openai.OpenAIModel.__init__),
so you can customise the `organization`, `project`, `base_url` etc. as defined in the [OpenAI API docs](https://platform.openai.com/docs/api-reference).

You could also use the [`AsyncAzureOpenAI`](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/switching-endpoints) client to use the Azure OpenAI API.

openai\_azure.py

```
from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

client = AsyncAzureOpenAI(
    azure_endpoint='...',
    api_version='2024-07-01-preview',
    api_key='your-api-key',
)

model = OpenAIModel('gpt-4o', openai_client=client)
agent = Agent(model)
...

```

## Anthropic

### Install

To use [`AnthropicModel`](https://ai.pydantic.dev/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel) models, you need to either install [`pydantic-ai`](https://ai.pydantic.dev/install/), or install [`pydantic-ai-slim`](https://ai.pydantic.dev/install/#slim-install) with the `anthropic` optional group:

[pip](https://ai.pydantic.dev/models/#__tabbed_2_1)[uv](https://ai.pydantic.dev/models/#__tabbed_2_2)

```
pip install 'pydantic-ai-slim[anthropic]'

```

```
uv add 'pydantic-ai-slim[anthropic]'

```

### Configuration

To use [Anthropic](https://anthropic.com/) through their API, go to [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) to generate an API key.

[`AnthropicModelName`](https://ai.pydantic.dev/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModelName) contains a list of available Anthropic models.

### Environment variable

Once you have the API key, you can set it as an environment variable:

```
export ANTHROPIC_API_KEY='your-api-key'

```

You can then use [`AnthropicModel`](https://ai.pydantic.dev/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel) by name:

anthropic\_model\_by\_name.py

```
from pydantic_ai import Agent

agent = Agent('claude-3-5-sonnet-latest')
...

```

Or initialise the model directly with just the model name:

anthropic\_model\_init.py

```
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

model = AnthropicModel('claude-3-5-sonnet-latest')
agent = Agent(model)
...

```

### `api_key` argument

If you don't want to or can't set the environment variable, you can pass it at runtime via the [`api_key` argument](https://ai.pydantic.dev/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel.__init__):

anthropic\_model\_api\_key.py

```
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

model = AnthropicModel('claude-3-5-sonnet-latest', api_key='your-api-key')
agent = Agent(model)
...

```

## Gemini

For prototyping only

Google themselves refer to this API as the "hobby" API, I've received 503 responses from it a number of times.
The API is easy to use and useful for prototyping and simple demos, but I would not rely on it in production.

If you want to run Gemini models in production, you should use the [VertexAI API](https://ai.pydantic.dev/models/#gemini-via-vertexai) described below.

### Install

To use [`GeminiModel`](https://ai.pydantic.dev/api/models/gemini/#pydantic_ai.models.gemini.GeminiModel) models, you just need to install [`pydantic-ai`](https://ai.pydantic.dev/install/) or [`pydantic-ai-slim`](https://ai.pydantic.dev/install/#slim-install), no extra dependencies are required.

### Configuration

[`GeminiModel`](https://ai.pydantic.dev/api/models/gemini/#pydantic_ai.models.gemini.GeminiModel) let's you use the Google's Gemini models through their [Generative Language API](https://ai.google.dev/api/all-methods), `generativelanguage.googleapis.com`.

[`GeminiModelName`](https://ai.pydantic.dev/api/models/gemini/#pydantic_ai.models.gemini.GeminiModelName) contains a list of available Gemini models that can be used through this interface.

To use `GeminiModel`, go to [aistudio.google.com](https://aistudio.google.com/) and follow your nose until you find the place to generate an API key.

### Environment variable

Once you have the API key, you can set it as an environment variable:

```
export GEMINI_API_KEY=your-api-key

```

You can then use [`GeminiModel`](https://ai.pydantic.dev/api/models/gemini/#pydantic_ai.models.gemini.GeminiModel) by name:

gemini\_model\_by\_name.py

```
from pydantic_ai import Agent

agent = Agent('google-gla:gemini-1.5-flash')
...

```

Note

The `google-gla` provider prefix represents the [Google **G** enerative **L** anguage **A** PI](https://ai.google.dev/api/all-methods) for `GeminiModel` s.
`google-vertex` is used with [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models) for `VertexAIModel` s.

Or initialise the model directly with just the model name:

gemini\_model\_init.py

```
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

model = GeminiModel('gemini-1.5-flash')
agent = Agent(model)
...

```

### `api_key` argument

If you don't want to or can't set the environment variable, you can pass it at runtime via the [`api_key` argument](https://ai.pydantic.dev/api/models/gemini/#pydantic_ai.models.gemini.GeminiModel.__init__):

gemini\_model\_api\_key.py

```
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

model = GeminiModel('gemini-1.5-flash', api_key='your-api-key')
agent = Agent(model)
...

```

## Gemini via VertexAI

To run Google's Gemini models in production, you should use [`VertexAIModel`](https://ai.pydantic.dev/api/models/vertexai/#pydantic_ai.models.vertexai.VertexAIModel) which uses the `*-aiplatform.googleapis.com` API.

[`GeminiModelName`](https://ai.pydantic.dev/api/models/gemini/#pydantic_ai.models.gemini.GeminiModelName) contains a list of available Gemini models that can be used through this interface.

### Install

To use [`VertexAIModel`](https://ai.pydantic.dev/api/models/vertexai/#pydantic_ai.models.vertexai.VertexAIModel), you need to either install [`pydantic-ai`](https://ai.pydantic.dev/install/), or install [`pydantic-ai-slim`](https://ai.pydantic.dev/install/#slim-install) with the `vertexai` optional group:

[pip](https://ai.pydantic.dev/models/#__tabbed_3_1)[uv](https://ai.pydantic.dev/models/#__tabbed_3_2)

```
pip install 'pydantic-ai-slim[vertexai]'

```

```
uv add 'pydantic-ai-slim[vertexai]'

```

### Configuration

This interface has a number of advantages over `generativelanguage.googleapis.com` documented above:

1. The VertexAI API is more reliably and marginally lower latency in our experience.
2. You can
    [purchase provisioned throughput](https://cloud.google.com/vertex-ai/generative-ai/docs/provisioned-throughput#purchase-provisioned-throughput)
    with VertexAI to guarantee capacity.
3. If you're running PydanticAI inside GCP, you don't need to set up authentication, it should "just work".
4. You can decide which region to use, which might be important from a regulatory perspective,
    and might improve latency.

The big disadvantage is that for local development you may need to create and configure a "service account", which I've found extremely painful to get right in the past.

Whichever way you authenticate, you'll need to have VertexAI enabled in your GCP account.

### Application default credentials

Luckily if you're running PydanticAI inside GCP, or you have the [`gcloud` CLI](https://cloud.google.com/sdk/gcloud) installed and configured, you should be able to use `VertexAIModel` without any additional setup.

To use `VertexAIModel`, with [application default credentials](https://cloud.google.com/docs/authentication/application-default-credentials) configured (e.g. with `gcloud`), you can simply use:

vertexai\_application\_default\_credentials.py

```
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

model = VertexAIModel('gemini-1.5-flash')
agent = Agent(model)
...

```

Internally this uses [`google.auth.default()`](https://google-auth.readthedocs.io/en/master/reference/google.auth.html) from the `google-auth` package to obtain credentials.

Won't fail until `agent.run()`

Because `google.auth.default()` requires network requests and can be slow, it's not run until you call `agent.run()`. Meaning any configuration or permissions error will only be raised when you try to use the model. To initialize the model for this check to be run, call [`await model.ainit()`](https://ai.pydantic.dev/api/models/vertexai/#pydantic_ai.models.vertexai.VertexAIModel.ainit).

You may also need to pass the [`project_id` argument to `VertexAIModel`](https://ai.pydantic.dev/api/models/vertexai/#pydantic_ai.models.vertexai.VertexAIModel.__init__) if application default credentials don't set a project, if you pass `project_id` and it conflicts with the project set by application default credentials, an error is raised.

### Service account

If instead of application default credentials, you want to authenticate with a service account, you'll need to create a service account, add it to your GCP project (note: AFAIK this step is necessary even if you created the service account within the project), give that service account the "Vertex AI Service Agent" role, and download the service account JSON file.

Once you have the JSON file, you can use it thus:

vertexai\_service\_account.py

```
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

model = VertexAIModel(
    'gemini-1.5-flash',
    service_account_file='path/to/service-account.json',
)
agent = Agent(model)
...

```

### Customising region

Whichever way you authenticate, you can specify which region requests will be sent to via the [`region` argument](https://ai.pydantic.dev/api/models/vertexai/#pydantic_ai.models.vertexai.VertexAIModel.__init__).

Using a region close to your application can improve latency and might be important from a regulatory perspective.

vertexai\_region.py

```
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

model = VertexAIModel('gemini-1.5-flash', region='asia-east1')
agent = Agent(model)
...

```

[`VertexAiRegion`](https://ai.pydantic.dev/api/models/vertexai/#pydantic_ai.models.vertexai.VertexAiRegion) contains a list of available regions.

## Ollama

### Install

To use [`OllamaModel`](https://ai.pydantic.dev/api/models/ollama/#pydantic_ai.models.ollama.OllamaModel), you need to either install [`pydantic-ai`](https://ai.pydantic.dev/install/), or install [`pydantic-ai-slim`](https://ai.pydantic.dev/install/#slim-install) with the `openai` optional group:

[pip](https://ai.pydantic.dev/models/#__tabbed_4_1)[uv](https://ai.pydantic.dev/models/#__tabbed_4_2)

```
pip install 'pydantic-ai-slim[openai]'

```

```
uv add 'pydantic-ai-slim[openai]'

```

**This is because internally, `OllamaModel` uses the OpenAI API.**

### Configuration

To use [Ollama](https://ollama.com/), you must first download the Ollama client, and then download a model using the [Ollama model library](https://ollama.com/library).

You must also ensure the Ollama server is running when trying to make requests to it. For more information, please see the [Ollama documentation](https://github.com/ollama/ollama/tree/main/docs).

For detailed setup and example, please see the [Ollama setup documentation](https://github.com/pydantic/pydantic-ai/blob/main/docs/api/models/ollama.md).

## Groq

### Install

To use [`GroqModel`](https://ai.pydantic.dev/api/models/groq/#pydantic_ai.models.groq.GroqModel), you need to either install [`pydantic-ai`](https://ai.pydantic.dev/install/), or install [`pydantic-ai-slim`](https://ai.pydantic.dev/install/#slim-install) with the `groq` optional group:

[pip](https://ai.pydantic.dev/models/#__tabbed_5_1)[uv](https://ai.pydantic.dev/models/#__tabbed_5_2)

```
pip install 'pydantic-ai-slim[groq]'

```

```
uv add 'pydantic-ai-slim[groq]'

```

### Configuration

To use [Groq](https://groq.com/) through their API, go to [console.groq.com/keys](https://console.groq.com/keys) and follow your nose until you find the place to generate an API key.

[`GroqModelName`](https://ai.pydantic.dev/api/models/groq/#pydantic_ai.models.groq.GroqModelName) contains a list of available Groq models.

### Environment variable

Once you have the API key, you can set it as an environment variable:

```
export GROQ_API_KEY='your-api-key'

```

You can then use [`GroqModel`](https://ai.pydantic.dev/api/models/groq/#pydantic_ai.models.groq.GroqModel) by name:

groq\_model\_by\_name.py

```
from pydantic_ai import Agent

agent = Agent('groq:llama-3.3-70b-versatile')
...

```

Or initialise the model directly with just the model name:

groq\_model\_init.py

```
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

model = GroqModel('llama-3.3-70b-versatile')
agent = Agent(model)
...

```

### `api_key` argument

If you don't want to or can't set the environment variable, you can pass it at runtime via the [`api_key` argument](https://ai.pydantic.dev/api/models/groq/#pydantic_ai.models.groq.GroqModel.__init__):

groq\_model\_api\_key.py

```
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

model = GroqModel('llama-3.3-70b-versatile', api_key='your-api-key')
agent = Agent(model)
...

```

## Mistral

### Install

To use [`MistralModel`](https://ai.pydantic.dev/api/models/mistral/#pydantic_ai.models.mistral.MistralModel), you need to either install [`pydantic-ai`](https://ai.pydantic.dev/install/), or install [`pydantic-ai-slim`](https://ai.pydantic.dev/install/#slim-install) with the `mistral` optional group:

[pip](https://ai.pydantic.dev/models/#__tabbed_6_1)[uv](https://ai.pydantic.dev/models/#__tabbed_6_2)

```
pip install 'pydantic-ai-slim[mistral]'

```

```
uv add 'pydantic-ai-slim[mistral]'

```

### Configuration

To use [Mistral](https://mistral.ai/) through their API, go to [console.mistral.ai/api-keys/](https://console.mistral.ai/api-keys/) and follow your nose until you find the place to generate an API key.

[`NamedMistralModels`](https://ai.pydantic.dev/api/models/mistral/#pydantic_ai.models.mistral.NamedMistralModels) contains a list of the most popular Mistral models.

### Environment variable

Once you have the API key, you can set it as an environment variable:

```
export MISTRAL_API_KEY='your-api-key'

```

You can then use [`MistralModel`](https://ai.pydantic.dev/api/models/mistral/#pydantic_ai.models.mistral.MistralModel) by name:

mistral\_model\_by\_name.py

```
from pydantic_ai import Agent

agent = Agent('mistral:mistral-large-latest')
...

```

Or initialise the model directly with just the model name:

mistral\_model\_init.py

```
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel

model = MistralModel('mistral-small-latest')
agent = Agent(model)
...

```

### `api_key` argument

If you don't want to or can't set the environment variable, you can pass it at runtime via the [`api_key` argument](https://ai.pydantic.dev/api/models/mistral/#pydantic_ai.models.mistral.MistralModel.__init__):

mistral\_model\_api\_key.py

```
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel

model = MistralModel('mistral-small-latest', api_key='your-api-key')
agent = Agent(model)
...

```

## OpenAI-compatible Models

Many of the models are compatible with OpenAI API, and thus can be used with [`OpenAIModel`](https://ai.pydantic.dev/api/models/openai/#pydantic_ai.models.openai.OpenAIModel) in PydanticAI.
Before getting started, check the [OpenAI](https://ai.pydantic.dev/models/#openai) section for installation and configuration instructions.

To use another OpenAI-compatible API, you can make use of the [`base_url`](https://ai.pydantic.dev/api/models/openai/#pydantic_ai.models.openai.OpenAIModel.__init__) and [`api_key`](https://ai.pydantic.dev/api/models/openai/#pydantic_ai.models.openai.OpenAIModel.__init__) arguments:

openai\_model\_base\_url.py

```
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    'model_name',
    base_url='https://<openai-compatible-api-endpoint>.com',
    api_key='your-api-key',
)
...

```

### OpenRouter

To use [OpenRouter](https://openrouter.ai/), first create an API key at [openrouter.ai/keys](https://openrouter.ai/keys).

Once you have the API key, you can pass it to [`OpenAIModel`](https://ai.pydantic.dev/api/models/openai/#pydantic_ai.models.openai.OpenAIModel) as the `api_key` argument:

openrouter\_model\_init.py

```
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    'anthropic/claude-3.5-sonnet',
    base_url='https://openrouter.ai/api/v1',
    api_key='your-openrouter-api-key',
)
agent = Agent(model)
...

```

### Grok (xAI)

Go to [xAI API Console](https://console.x.ai/) and create an API key.
Once you have the API key, follow the [xAI API Documentation](https://docs.x.ai/docs/overview), and set the `base_url` and `api_key` arguments appropriately:

grok\_model\_init.py

```
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    'grok-2-1212',
    base_url='https://api.x.ai/v1',
    api_key='your-xai-api-key',
)
agent = Agent(model)
...

```

### DeepSeek

Go to [DeepSeek API Platform](https://platform.deepseek.com/api_keys) and create an API key.
Once you have the API key, follow the [DeepSeek API Documentation](https://platform.deepseek.com/docs/api/overview), and set the `base_url` and `api_key` arguments appropriately:

deepseek\_model\_init.py

```
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

model = OpenAIModel(
    'deepseek-chat',
    base_url='https://api.deepseek.com',
    api_key='your-deepseek-api-key',
)
agent = Agent(model)
...

```

## Implementing Custom Models

To implement support for models not already supported, you will need to subclass the [`Model`](https://ai.pydantic.dev/api/models/base/#pydantic_ai.models.Model) abstract base class.

This in turn will require you to implement the following other abstract base classes:

- [`AgentModel`](https://ai.pydantic.dev/api/models/base/#pydantic_ai.models.AgentModel)
- [`StreamedResponse`](https://ai.pydantic.dev/api/models/base/#pydantic_ai.models.StreamedResponse)

The best place to start is to review the source code for existing implementations, e.g. [`OpenAIModel`](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/models/openai.py).

For details on when we'll accept contributions adding new models to PydanticAI, see the [contributing guidelines](https://ai.pydantic.dev/contributing/#new-model-rules).