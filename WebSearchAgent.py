import os
from rich import print
from typing import Optional, TypedDict, List
from os.path import join, exists
from os import listdir, makedirs
from datetime import datetime
from google import genai
from google.genai import types
from openai import OpenAI
from pydantic import BaseModel, Field
from config import Config
import asyncio
from crawl4ai import *
from pydantic_ai import Agent, UnexpectedModelBehavior, capture_run_messages
from pydantic_ai.models.gemini import GeminiModel
from dataclasses import dataclass
import requests
import json

from threading import Lock

class ToolRegistry:
    _tools = {}
    _lock = Lock()
    
    @classmethod
    def register(cls, name: str, description: str = None, category: str = "search"):
        def decorator(func):
            func.metadata = {
                "name": name,
                "description": description or func.__doc__,
                "category": category
            }
            with cls._lock:
                cls._tools[name] = func
            return func
        return decorator
    
    @classmethod
    def get_tools(cls, tool_names: List[str]):
        tools = []
        for name in tool_names:
            if name not in cls._tools:
                raise ValueError(f"Tool '{name}' not registered")
            tools.append(cls._tools[name])
        return tools

class Response(BaseModel):
    additional_notes: str = Field(description="Additional notes or observations.")
     
flash1_model = "gemini-1.5-flash"
flash2_model = "gemini-2.0-flash-exp"
model = GeminiModel(flash2_model)

system_prompt = """abc"""
agent = Agent(
    model,
    result_type=Response,
    system_prompt=system_prompt
    )

async def crawl_website_async(url_webpage):
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

@ToolRegistry.register("google_general")
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
import httpx

async def google_general_search_async(search_query: str, time_span: Optional[str] = None) -> Optional[dict]:
    """Async version of google_general_search"""
    if not search_query.strip():
        raise ValueError("Search query cannot be empty")
    if time_span and time_span not in ["qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y"]:
        raise ValueError("Invalid time span value")

    num_results = 10
    api_key = os.environ.get("SERPER_API_KEY")

    if not api_key:
        print("SERPER_API_KEY not found in environment variables.")
        return

    url = "https://google.serper.dev/search"
    
    payload = {
        "q": search_query,
        "num": num_results
    }
    
    if time_span:
        payload["tbs"] = time_span
        
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def google_general_search(search_query: str, time_span: Optional[str] = None) -> Optional[dict]:
    """Uses the Serper API to retrieve google results based on a string query.
    
    Raises:
        ValueError: If search query is empty or time_span is invalid
        HTTPError: If the API request fails
    Certain search results could be faulty or irrelevant, please ignore these results.

    Args:
        search_query (str): The google query string. It needs to be suited for the given research topic.
        time_span (str, optional): Time filter for search results. Options:
            - "qdr:h" (Past hour)
            - "qdr:d" (Past 24 hours)
            - "qdr:w" (Past Week)
            - "qdr:m" (Past Month)
            - "qdr:y" (Past Year)
            If None, no time filter is applied.
    
    Returns:
        document_data: A dictionary with the following fields:
            - 'topic': The research topic (=search_query)
            - 'link': The webpage link
            - 'snippet': A short snippet of the webpage
            - 'date': The date of the webpage
            - 'position': Element position
            - 'markdown': The markdown text (webpage content)
            - 'filename': filename (saved in folder with name=topic_folder_name)
    """
    if not search_query.strip():
        raise ValueError("Search query cannot be empty")
    if time_span and time_span not in ["qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y"]:
        raise ValueError("Invalid time span value")
        
    num_results = 10
    api_key = os.environ.get("SERPER_API_KEY")

    if not api_key:
        print("SERPER_API_KEY not found in environment variables.")
        return

    url = "https://google.serper.dev/search"
    
    payload = {
        "q": search_query,
        "num": num_results
    }
    
    if time_span:
        payload["tbs"] = time_span
        
    payload = json.dumps(payload)

    headers = {
    'X-API-KEY': api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response.raise_for_status()  # Will raise HTTPError for 4xx/5xx responses
    json_response = response.json()

    return json_response

@ToolRegistry.register("scholar")
def google_scholar_search(search_query: str, topic_folder_name: str, time_span: str = None, num_pages: int = 1) -> dict:
    """Uses the Serper API to retrieve google scholar results based on a string query.
    Certain search results could be faulty or irrelevant, please ignore these results.

    Args:
        search_query (str): The google query string. It needs to be suited for the given research topic.
        topic_folder_name (str): Name of the topic folder
        time_span (str, optional): Time span for the search. Defaults to None.
        num_pages (int, optional): Number of pages to retrieve. Defaults to 1.

    Returns:
        dict: List of papers from all requested pages
    """

    url = "https://google.serper.dev/scholar"
    page = 1
    papers = []

    for _ in range(num_pages):
        payload = json.dumps({
            "q": search_query,
            "page": page,
            "tbs": time_span
        }) if time_span else json.dumps({"q": search_query, "page": page})
        headers = {
            'X-API-KEY': Config.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 200:
            print(f"Scholar search failed with status {response.status_code}")
            return []
        json_response = json.loads(response.text)
        organic = json_response['organic']
        papers.extend(organic)
        page += 1

    return papers

class PerplexityResult(TypedDict):
    test_response: str
    citations: list[str]

@ToolRegistry.register("perplexity")
def perplexity_search(search_query: str) -> PerplexityResult | None:
    """Uses the Perplexity API to perform a search and generate a response with citations.

    Args:
        search_query (str): The query string for Perplexity. It should be crafted to
            effectively utilize Perplexity's LLM processing of web content.

    Returns:
        PerplexityResult | None: A dictionary containing:
            - 'test_response' (str): The text response from Perplexity, including citations
            - 'citations' (list[str]): List of citation URLs
            Returns None if the search fails.
    """
    messages = [
        {
            "role": "system",
            "content": "You are an artificial intelligence assistant that engages in helpful, detailed conversations.",
        },
        {   
            "role": "user",
            "content": search_query,
        },
    ]

    try:
        client = OpenAI(
            api_key=Config.PERPLEXITY_API_KEY, 
            base_url=Config.PERPLEXITY_BASE_URL
        )

        response = client.chat.completions.create(
            model="sonar-pro",
            messages=messages,
        )

        message = response.choices[0].message.content + "\n\n"
        citations = [citation['url'] for citation in response.citations] if hasattr(response, 'citations') else []

        # Format citations in the message
        for i, url in enumerate(citations, 1):
            message += f"[{i}] {url}\n"

        return {
            'test_response': message.strip(),
            'citations': citations
        }

    except Exception as e:
        print(f"Perplexity search failed: {e}")
        return None

@ToolRegistry.register("papers_with_code")
def papers_with_code_search(query: str, items_per_page: int = 200) -> dict | None:
    """
    Search papers with the given query and return the results as a dictionary.

    Args:
        query (str): The query string to search for.
        items_per_page (int): The number of items to return per page (default is 200).

    Returns:
        dict: A dictionary with the following keys:
            - 'count': The total number of results found.
            - 'results': A list of dictionaries, each representing a search result.
                - 'paper': The paper title.
                - 'repository': The repository URL.
                - 'is_official': Whether the paper is official.
            - 'paper': A dictionary with the following keys
                 - ['id', 'arxiv_id', 'nips_id', 'url_abs', 'url_pdf', 'title', 'abstract', 
                 'authors', 'published', 'conference', 'conference_url_abs', 
                 'conference_url_pdf', 'proceeding'])
    """
    
    params = {
        "page": 1,
        "items_per_page": items_per_page,
        "q": query  # Space will be auto-encoded to "%20"
    }

    headers = {
        "accept": "application/json",
        "X-CSRFToken": Config.PAPERS_WITH_CODE_CSRF_TOKEN
    }

    try:
        # Send GET request
        response = requests.get("https://paperswithcode.com/api/v1/search/", 
                                params=params, 
                                headers=headers)

        response.raise_for_status()  # Raise exception for HTTP errors (e.g., 4xx/5xx)
        
        # Parse JSON response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"Failed to parse JSON: {e}")
        return None

def initialize_agent(selected_tools: List[str] = None):
    global agent
    if selected_tools is None:
        selected_tools = list(ToolRegistry._tools.keys())
        
    # Create base agent first
    agent = Agent(
        model,
        result_type=Response,
        system_prompt=system_prompt
    )
    
    # Register selected tools
    for tool_func in ToolRegistry.get_tools(selected_tools):
        agent.tool_plain(tool_func)

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
