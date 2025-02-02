import os
from enum import StrEnum
from typing import Optional, TypedDict, List
import httpx
from config import Config
import requests
import json
from openai import AsyncOpenAI, BaseModel
from firecrawl import FirecrawlApp
from agent_utils import *
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from openai import OpenAI
from openai import AsyncOpenAI

config = Config()

class TimeSpan(StrEnum):
    """
    Time span specification for Google search using Pydantic StrEnum.
    """
    HOUR = "qdr:h"
    DAY = "qdr:d"
    WEEK = "qdr:w"
    MONTH = "qdr:m"
    YEAR = "qdr:y"


async def google_general_search_async(search_query: str, time_span: Optional[TimeSpan] = None, web_domain: Optional[str] = None) -> Optional[dict]:
    """
    Perform a Google search using the Serper API.
    
    Args:
        search_query (str): The search query string.
        time_span (Optional[TimeSpan], optional): The time span. Defaults to None.
            - Allowed:
                - "qdr:h" (for hour)
                - "qdr:d" (for day)
                - "qdr:w" (for week)
                - "qdr:m" (for month)
                - "qdr:y" (for year)
        web_domain (Optional[str], optional): Search inside a web domain (e.g., web_domain="brainchip.com" -> searches only pages with this domain)
    Returns:
        Optional[dict]: The search results.
    """

    if web_domain and ("site:" not in search_query):
        if "site:" not in web_domain:
            web_domain = f"site:{web_domain}"
        search_query = f"{web_domain} {search_query}"

    if not search_query.strip():
        raise ValueError("Search query cannot be empty")
    if time_span and time_span not in ["qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y"]:
        raise ValueError(f"Invalid time span value: {time_span}")

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

async def google_scholar_search_async(search_query: str, num_pages: int = 1) -> dict:
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
                config.SERPER_BASE_URL,
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

async def google_news_search_async(search_query: str, num_pages: int = 1) -> dict:
    """Async version of google news search using Serper API
    
    Args:
        search_query (str): The search query to use
        num_pages (int, optional): Number of pages to fetch. Defaults to 1.
        
    Returns:
        dict: List of news articles found
    """
    page = 1
    news_articles = []

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
                config.SERPER_BASE_URL,
                headers=headers,
                data=payload
            )
            if response.status_code != 200:
                print(f"News search failed with status {response.status_code}")
                return []
            json_response = response.json()
            news_articles.extend(json_response.get('news', []))
            page += 1

    return news_articles

class PerplexityResult(TypedDict):
    text_response: str
    citations: list[str]

async def perplexity_search_async(search_query: str) -> PerplexityResult | None:
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

        response = PerplexityResult(
            text_response = message.strip(),
            citations=response.citations
        )

        return response
    except Exception as e:
        print(f"Perplexity search failed: {e}")
        return None

def perplexity_sonar_reasoning(search_query: str) -> PerplexityResult | None:

    try:
        client = OpenAI(
        base_url=config.OPENROUTER_BASE_URL,
        api_key=config.OPENROUTER_API_KEY,
        )

        completion = client.chat.completions.create(
        model=config.OPENROUTER_PERPLEXITY_SONAR_REASONING,
        messages=[
            {
            "role": "user",
            "content": search_query
            }
        ])

        response = PerplexityResult(
                text_response = completion.choices[0].message.content.strip(),
                citations=completion.citations
            )

        return response
    except Exception as e:
        print(f"Perplexity search failed: {e}")
        return None

async def papers_with_code_search_async(query: str, items_per_page: int = 200) -> dict | None:
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

async def map_website_async(url: str, include_subdomains: bool = True) -> dict | None:
    """Map a website's content using FirecrawlApp.
    
    Args:
        url (str): The URL to map
        include_subdomains (bool, optional): Whether to include subdomains in the mapping. Defaults to True.
        
    Returns:
        dict | None: The mapping results or None if the operation fails
    """
    try:
        app = FirecrawlApp(api_key=config.FIRECRAWL_API_KEY)
        result = app.map_url(url, params={
            'includeSubdomains': include_subdomains
        })
        return result
    except Exception as e:
        print(f"Website mapping failed: {e}")
        return None

async def scrape_website_async(url: str) -> dict | None:
    """Scrape a website's content using FirecrawlApp.
    
    Args:
        url (str): The URL to scrape
        
    Returns:
        dict | None: The scraping results or None if the operation fails
    """
    try:
        app = FirecrawlApp(api_key=config.FIRECRAWL_API_KEY)
        result = app.scrape_url(url, params={
            'formats': ['markdown']
        })
        return result
    except Exception as e:
        print(f"Website scraping failed: {e}")
        return None

async def crawl_website_async(url: str, limit: int = 10) -> dict | None:
    """Crawl a website's content using FirecrawlApp.
    
    Args:
        url (str): The URL to crawl
        limit (int, optional): Maximum number of pages to crawl. Defaults to 10.
        
    Returns:
        dict | None: The crawling results or None if the operation fails
    """
    try:
        app = FirecrawlApp(api_key=config.FIRECRAWL_API_KEY)
        result = app.crawl_url(url, params={
            'limit': limit,
            'scrapeOptions': {
                'formats': ['markdown']
            }
        })
        return result
    except Exception as e:
        print(f"Website crawling failed: {e}")
        return None

async def crawl4ai_website_async(url_webpage: str) -> str:

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

def crawl_website_async(url_webpage):
    return asyncio.run(crawl4ai_website_async(url_webpage))

class ReasoningModelResponse(BaseModel):
    reasoning_content: str = Field(description="The reasoning/thinking chain-of-thought output of the model.")
    final_answer: str = Field(description="The final response/answer of the model (after thinking).")

def deepseekR1_call(user_input: str) -> ReasoningModelResponse:
    """
    Call the DeepSeek Reasoner model to process user input.

    This function sends a user query to the DeepSeek Reasoner model and processes
    the streamed response, separating the reasoning content from the final answer.

    Args:
        user_input (str): The user's query or input to be processed by the model.

    Returns:
        DeepseekR1Response: An object containing the reasoning content and final answer.

    Raises:
        Exception: If there's an error in API communication or response processing.
    """

    deepseek_client = OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL
    )
    model = config.DEEPSEEK_R1

    deepseek_messages = []
    deepseek_messages.append({
        "role": "user", 
        "content": user_input
        })
    
    response = deepseek_client.chat.completions.create(
                model=model,
                #max_tokens=1,
                messages=deepseek_messages,
                stream=True
            )

    reasoning_content = ""
    final_content = ""

    for chunk in response:
        if chunk.choices[0].delta.reasoning_content:
            reasoning_piece = chunk.choices[0].delta.reasoning_content
            reasoning_content += reasoning_piece
        elif chunk.choices[0].delta.content:
            final_content += chunk.choices[0].delta.content

    response = ReasoningModelResponse(
        reasoning_content=reasoning_content, 
        final_answer=final_content)
    return response        

def free_deepseekR1_call(user_input: str) -> ReasoningModelResponse:

    url = f"{config.OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": config.OPENROUTER_DEEPSEEK_R1,
        "messages": [
            {"role": "user", "content": user_input}
        ],
        "include_reasoning": True
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    thinking_part = response.json()['choices'][0]['message']['reasoning']
    final_answer = response.json()['choices'][0]['message']['content']

    response = ReasoningModelResponse(
        reasoning_content=thinking_part, 
        final_answer=final_answer)
    return response 

def gemini_flash2_thinking_call(user_input: str) -> ReasoningModelResponse:
    
    # Only run this block for Gemini Developer API
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    response = client.models.generate_content(
        model=config.FLASH2_MODEL_THINKING,
        contents=user_input,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(include_thoughts=True),
            http_options=types.HttpOptions(api_version='v1alpha'),
        )
    )
    thinking_part = response.candidates[0].content.parts[0].text
    final_answer = response.candidates[0].content.parts[1].text

    response = ReasoningModelResponse(
        reasoning_content=thinking_part, 
        final_answer=final_answer)
    return response 