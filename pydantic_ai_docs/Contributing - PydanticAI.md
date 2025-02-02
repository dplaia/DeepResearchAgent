[Skip to content](https://ai.pydantic.dev/contributing/#installation-and-setup)

Version Notice


This documentation is ahead of the last release by
[13 commits](https://github.com/pydantic/pydantic-ai/compare/v0.0.20...main).
You may see documentation for features not yet supported in the latest release [v0.0.20 2025-01-23](https://github.com/pydantic/pydantic-ai/releases/tag/v0.0.20).


# Contributing

We'd love you to contribute to PydanticAI!

## Installation and Setup

Clone your fork and cd into the repo directory

```
git clone git@github.com:<your username>/pydantic-ai.git
cd pydantic-ai

```

Install `uv` (version 0.4.30 or later) and `pre-commit`

We use pipx here, for other options see:

- [`uv` install docs](https://docs.astral.sh/uv/getting-started/installation/)
- [`pre-commit` install docs](https://pre-commit.com/#install)

To get `pipx` itself, see [these docs](https://pypa.github.io/pipx/)

```
pipx install uv pre-commit

```

Install `pydantic-ai`, all dependencies and pre-commit hooks

```
make install

```

## Running Tests etc.

We use `make` to manage most commands you'll need to run.

For details on available commands, run:

```
make help

```

To run code formatting, linting, static type checks, and tests with coverage report generation, run:

```
make

```

## Documentation Changes

To run the documentation page locally, run:

```
uv run mkdocs serve

```

## Rules for adding new models to PydanticAI

To avoid an excessive workload for the maintainers of PydanticAI, we can't accept all model contributions, so we're setting the following rules for when we'll accept new models and when we won't. This should hopefully reduce the chances of disappointment and wasted work.

- To add a new model with an extra dependency, that dependency needs > 500k monthly downloads from PyPI consistently over 3 months or more
- To add a new model which uses another models logic internally and has no extra dependencies, that model's GitHub org needs > 20k stars in total
- For any other model that's just a custom URL and API key, we're happy to add a one-paragraph description with a link and instructions on the URL to use
- For any other model that requires more logic, we recommend you release your own Python package `pydantic-ai-xxx`, which depends on [`pydantic-ai-slim`](https://ai.pydantic.dev/install/#slim-install) and implements a model that inherits from our [`Model`](https://ai.pydantic.dev/api/models/base/#pydantic_ai.models.Model) ABC

If you're unsure about adding a model, please [create an issue](https://github.com/pydantic/pydantic-ai/issues).