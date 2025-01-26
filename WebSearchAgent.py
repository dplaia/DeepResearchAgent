import os
from rich import print
from typing import Optional, TypedDict, List
from os.path import join, exists
from os import listdir, makedirs
from datetime import datetime
from google import genai
from google.genai import types
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from config import Config
import asyncio
from crawl4ai import *
from pydantic_ai import Agent, UnexpectedModelBehavior, capture_run_messages
from pydantic_ai.models.gemini import GeminiModel
from dataclasses import dataclass
import requests
import json
import httpx

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

async def crawl_website_async(url_webpage: str):

    """
    Crawl a website using the crawl4ai library.
    
    Args:
        url_webpage (str): The URL of the webpage to crawl.
    
    Returns:
        str: The crawled content in markdown format.
    """
    
    if is_pdf_url(url_webpage):
        md = MarkItDown()
        result = md.convert(url_webpage)
        
        return result.text_content
        
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url_webpage,
        )
        return result.markdown

def crawl_website(url_webpage):
    return asyncio.run(crawl_website_async(url_webpage))
    
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

async def google_general_search(search_query: str, time_span: Optional[str] = None) -> Optional[dict]:
    """Async version of google_general_search"""
    if not search_query.strip():
        raise ValueError("Search query cannot be empty")
    if time_span and time_span not in ["qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y"]:
        raise ValueError("Invalid time span value")

    num_results = 10

    payload = {
        "q": search_query,
        "num": num_results
    }
    
    if time_span:
        payload["tbs"] = time_span
        
    headers = {
        'X-API-KEY': config.SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(config.SERPER_BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

async def google_scholar_search(search_query: str, num_pages: int = 1) -> dict:
    """Async version of google scholar search"""
    page = 1
    papers = []

    async with httpx.AsyncClient() as client:
        for _ in range(num_pages):
            payload = json.dumps({
                "q": search_query,
                "page": page
            })
            headers = {
                'X-API-KEY': config.SERPER_API_KEY,
                'Content-Type': 'application/json'
            }

            response = await client.post(
                config.SERPER_SCHOLAR_BASE_URL,
                headers=headers,
                data=payload
            )
            if response.status_code != 200:
                print(f"Scholar search failed with status {response.status_code}")
                return []
            json_response = response.json()
            papers.extend(json_response['organic'])
            page += 1

    return papers

class PerplexityResult(TypedDict):
    text_response: str
    citations: list[str]

async def perplexity_search(search_query: str) -> PerplexityResult | None:
    """Async version using AsyncOpenAI"""
    try:
        client = AsyncOpenAI(
            api_key=config.PERPLEXITY_API_KEY,
            base_url=config.PERPLEXITY_BASE_URL
        )

        response = await client.chat.completions.create(
            model="sonar-pro",
            messages=[{
                "role": "system",
                "content": "You are an artificial intelligence assistant that engages in helpful, detailed conversations.",
            }, {   
                "role": "user",
                "content": search_query,
            }],
        )

        message = response.choices[0].message.content + "\n\n"
        return {
            'text_response': message.strip(),
            'citations': response.citations
        }
    except Exception as e:
        print(f"Perplexity search failed: {e}")
        return None

async def papers_with_code_search(query: str, items_per_page: int = 200) -> dict | None:
    """Async version of papers with code search"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://paperswithcode.com/api/v1/search/",
                params={"items_per_page": items_per_page, "q": query},
                headers={"accept": "application/json", "X-CSRFToken": config.PAPERS_WITH_CODE_CSRF_TOKEN}
            )
            response.raise_for_status()
            data = response.json()
            sorted_list = sorted(data['results'], key=lambda x: x['repository']['stars'], reverse=True)
            data['results'] = sorted_list
            return data
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def initialize_agent(selected_tools: List[str] = None):
    global agent
    
    # Create tool list based on selection
    all_tools = {
        "google_general": google_general_search,
        "scholar": google_scholar_search,
        "perplexity": perplexity_search,
        "papers_with_code": papers_with_code_search
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
