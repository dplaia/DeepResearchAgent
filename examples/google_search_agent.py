from pydantic import BaseModel, Field
from crawl4ai import *
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import *
from agent_utils import *

from loguru import logger

config = Config()

console = Console()
# Log to a file with custom timestamp format
logger.add("agent_output.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
model = GeminiModel(config.FLASH2_MODEL)

async def run_agent(search_query):
    system_prompt = """
    You are a search expert that has access to a search tool/function.
    Use the search tool multiple times (if necessary) to find relevant links that might be useful for a given user prompt or search query.
    You can add as many links to the output list as you like (but not more than 10).
    """

    class SearchResponse(BaseModel):
        links: list[str] = Field(description="A list with relevant links (collection of links).")

    search_agent = Agent(
        model,
        result_type=SearchResponse,
        system_prompt=system_prompt)


    @search_agent.tool_plain
    async def google_search(search_query: str) -> dict:
        """Use the Google Search API to find results given a search query."""
        return await google_general_search_async(search_query)
        

    result = await search_agent.run(search_query)
    rprint(result.data.links)

    page_content_markdown = {}
    for link in result.data.links:
        #print(f"Link: {link}")
        markdown = await crawl4ai_website_async(link)
        page_content_markdown[link] = markdown

    combined_markdown = ""

    for (k, link) in enumerate(page_content_markdown.keys()):
        markdown = page_content_markdown[link]
        combined_markdown += f"From link ([{k+1}] {link}):\n\n{markdown}\n\n"


    combined_markdown = f""" Here is the search query of the user: 
    {search_query}

    Here is some content that might be useful to answer the user query:

    {combined_markdown}
    """

    system_prompt = """
    You are an expert at writing professional technical writer (articles, blogs, books, etc.).

    After receiving a user query and some files, your goal is to write an report about the user query.
    This writen report should be technically detailed but comprehensive for normal readers.

    Please use references in the report (e.g. [1]). You can find the link of a given input text above the text with "From link ([1] http ...)".

    Always use References at the end of the report.
    
    Write the output strictly in Markdown format. 
    """

    summary_agent = Agent(
        model,
        result_type=str,
        system_prompt=system_prompt)

    result = await summary_agent.run(combined_markdown)
    return result
    

if __name__ == "__main__":

    search_query = 'What are the most surprising facts about the new Deepseek R1 model?'
    result = asyncio.run(run_agent(search_query))


    console.print(Markdown(result.data))
