# DeepResearch


## Installation

In order to scrape webpages using crawl4AI with Playwright, you need to install Playwright with the following command:

```bash
source .venv/bin/activate
playwright install
```

## Usage

To use the DeepResearch system, follow these steps:

```bash
uv run extensive_search.py "How much energy is needed for one google search query?" -m 10 --save
```

The output of the script will be saved as markdown file called `markdown_output.md`, if `--save` is set to `True`.

With `-m` you can set how many individual searcher to perform (default = 5).


