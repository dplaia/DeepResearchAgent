import os
import json
from rich import print
from os.path import join, exists
from os import listdir, makedirs
from datetime import datetime
from google import genai
from google.genai import types
from openai import OpenAI
from pydantic import BaseModel, Field
import asyncio
from crawl4ai import *
from pydantic_ai import Agent, UnexpectedModelBehavior, capture_run_messages
from pydantic_ai.models.gemini import GeminiModel
from dataclasses import dataclass
import requests
import json

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
    
def save_files(topic_folder_name: str):
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

def google_general_search(search_query: str, time_span: str = None) -> dict:
    """Uses the Serper API to retrieve google results based on a string query.
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
    json_response = response.json()

    return json_response


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
            "page": page
        })
        headers = {
            'X-API-KEY': '27d67b7a71cfb66589271b1deffb5088822ff518',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        json_response = json.loads(response.text)
        organic = json_response['organic']
        papers.extend(organic)
        page += 1

    return papers



def perplexity_search(search_query: str) -> dict:
    """Uses the Serper API to retrieve google results based on a string query.
    Certain search results could be faulty or irrelevant, please ignore these results.

    Args:
        search_query (str): The Perplexity query string. Perplexity uses an LLM to do the processing of webpages. Use a query text that is most suitable for this.
    
    Returns:
        search_result: A dictionary with the following fields:
            - 'test_response' (str): The text response from the Perplexity LLM with citations in the form [1], [2], etc.
            - 'citations' (list[str]): A list of citations used in the test_response

    """

    test_response, citations = get_perplexity_search_results(search_query)

    search_result = {
        'test_response': test_response,
        'citations': citations
    }
    return search_result

def search_papers_with_code(query :str, items_per_page :int = 200) -> dict:
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
        "X-CSRFToken": "2ix1PR0FtUWIW5ePo08I3vhgHsvJ6fpqj0x1Ijjo4egxiofnUBzkX67bnHwbNd8G"
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

async def run_agent():
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
    # result = asyncio.run(run_agent())
    # print(result)

    data = search_papers_with_code("test-time compute")
    print("API Response:")
    print(data)