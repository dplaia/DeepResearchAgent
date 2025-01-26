import os
from rich import print
from typing import List
from os.path import join, exists
from os import makedirs
from pydantic import BaseModel, Field
from config import Config
import asyncio
from crawl4ai import *
from pydantic_ai import Agent, UnexpectedModelBehavior, capture_run_messages
from pydantic_ai.models.gemini import GeminiModel
from enum import StrEnum
from agent_tools import *
from agent_utils import *

class Response(BaseModel):
    additional_notes: str = Field(description="Additional notes or observations.")
     
config = Config()  # Create an instance of Config
model = GeminiModel(config.FLASH2_MODEL)

system_prompt = "abc"

agent = Agent(
    model,
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
        "perplexity": perplexity_search,
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

async def run_agent(selected_tools: List[str] = None):
    initialize_agent(selected_tools)  # Initialize with selected tools
    with capture_run_messages() as messages:  
        try:
            result = await agent.run('abc')
            print(result.all_messages())
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
    result = asyncio.run(run_agent(selected_tools))
    print(result)
