from enum import StrEnum
from typing import Optional, TypedDict, List
import httpx
from config import Config
import json
from openai import AsyncOpenAI
from firecrawl import FirecrawlApp
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

async def google_general_search(search_query: str, time_span: Optional[TimeSpan] = None, web_domain: Optional[str] = None) -> Optional[dict]:
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

    if web_domain & ("site:" not in search_query):
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

async def google_news_search(search_query: str, num_pages: int = 1) -> dict:
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

async def map_website(url: str, include_subdomains: bool = True) -> dict | None:
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
