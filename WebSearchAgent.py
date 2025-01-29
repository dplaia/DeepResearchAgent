
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from typing import List
from os.path import join, exists
from os import makedirs
from pydantic import BaseModel, Field
from config import Config
import asyncio
from crawl4ai import *
from pydantic_ai import Agent, UnexpectedModelBehavior, capture_run_messages
from pydantic_ai.models.gemini import GeminiModel
from agent_tools import *
from agent_utils import *

config = Config()  # Create an instance of Config
model = GeminiModel(config.FLASH2_MODEL)

class Response(BaseModel):
    text_response: str = Field(description="The text response of the agent.")
    additional_notes: str = Field(description="Additional notes or observations (optional).")
    tools_used: list[str] = Field(description="List all tools that you have used (e.g. Google Search, Papers With Code, etc.)")

system_prompt = """
You are a web search agent. Choose the search and crawling tools that available to you.
Write a report of the search results. Write it down as a form of a news article/blog post.

Use the webcrawler for links that you find in the search results but only if it seems useful.

Number of function calling are limited:

For news you can use:
- google_general_search (up to 3 calls)
- google_news_search  (up to 3 calls)

For scientific papers:
- google_scholar_search (up to 3 calls)
- papers_with_code_search  (up to 3 calls)

Web crawling:
- crawl_website_async (up to 2 calls in total).

If possible add citations. e.g. [1].

At the end of the document:
[1] www.example.com
[2] etc.

The output/formatting should be MarkDown. 
"""

class SomeOtherType(BaseModel):
    test: list[dict] = Field(description="some decription.")

class Deps(BaseModel):
    some_dependency: list[SomeOtherType]

agent = Agent(
    model,
    # deps_type=Deps, (optional)
    result_type=Response,
    system_prompt=system_prompt
    )


def save_files(topic_folder_name: str, json_response: dict, search_query: str):
    # Create folder if not exists
    if not exists(topic_folder_name):
        makedirs(topic_folder_name)

    document_data = {}

    for result in json_response['organic']:
        title = result.get('title', '').replace("/", " - ")
        link = result.get('link', '')
        markdown = crawl_website(link) if link else ''
        filename = title + ".md"

        document_data[title] = {
            'topic': search_query,
            'link': link,
            'snippet': result.get('snippet', ''),
            'date': result.get('date', ''),
            'position': result.get('position', 0),
            'markdown': markdown,
            'filename': filename
        }

        with open(join(topic_folder_name, filename), "w") as f:
            f.write(markdown)


def initialize_agent(selected_tools: List[str] = None):
    global agent
    
    # Create tool list based on selection
    all_tools = {
        "google_general": google_general_search,
        "scholar": google_scholar_search,
        #"perplexity": perplexity_search,
        "papers_with_code": papers_with_code_search,
        "news": google_news_search
    }
    
    selected = selected_tools or list(all_tools.keys())
    tools_list = [all_tools[name] for name in selected]

    # Create agent with selected tools
    agent = Agent(
        model,
        result_type=Response,
        system_prompt=system_prompt,
        tools=tools_list
    )


async def run_agent(search_query: str, selected_tools: List[str] = None):
    initialize_agent(selected_tools)  # Initialize with selected tools

    with capture_run_messages() as messages:  
        try:
            
            result = await agent.run(search_query)

            # Create a console instance
            console = Console()

            md = Markdown(result.data.text_response)
            console.print(md)

            rprint(result.data.tools_used)
        except UnexpectedModelBehavior as e:
            print('An error occurred:', e)
            #> An error occurred: Tool exceeded max retries count of 1
            print('Cause:', repr(e.__cause__))
            #> cause: ModelRetry('Please try again.')
            #print('Messages:', messages)
            pprint(vars(messages[0]))

        else:
            print(f"Result: {result.data}")
    return result

if __name__ == "__main__":
    # Example: Select specific tools to enable
    selected_tools = ["google_general", "perplexity"]
    #tools_list = [google_general_search, google_scholar_search, papers_with_code_search, crawl_website_async, google_news_search] #perplexity_search,
    search_query = "What are considered good hearing devices?"
    result = asyncio.run(run_agent(search_query, selected_tools))
    print(result)
