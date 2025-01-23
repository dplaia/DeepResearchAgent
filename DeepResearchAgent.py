import os
import time
from os.path import join, exists
from os import listdir, makedirs
from datetime import datetime
from google import genai
from google.genai import types
from openai import OpenAI
import requests
import json
from pydantic import BaseModel, Field
import asyncio
from crawl4ai import *
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from pydantic_ai.models.gemini import GeminiModel
from datetime import date
from tqdm import tqdm  # For progress bar

def is_pdf_url(url, timeout=5):
    try:
        # Try HEAD first to avoid downloading content
        response = requests.head(url, allow_redirects=True, timeout=timeout)

        # Fallback to GET if HEAD not allowed
        if response.status_code == 405:
            response = requests.get(url, stream=True, timeout=timeout)

        content_type = response.headers.get('Content-Type', '').lower()
        return 'application/pdf' in content_type

    except requests.exceptions.RequestException:
        return False

def download_pdf(pdf_url, filename="downloaded_pdf.pdf", download_dir=".", timeout=10):
    """Downloads a PDF file from a given URL and saves it locally with enhanced features.

    Args:
        pdf_url: The URL of the PDF file.
        filename: The name to save the PDF file as (optional, defaults to "downloaded_pdf.pdf").
        download_dir: The directory to save the PDF file to (optional, defaults to current directory).
        timeout:  Timeout in seconds for the request (optional, defaults to 10 seconds).
    """
    try:
        response = requests.get(pdf_url, stream=True, timeout=timeout) # Added timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        file_path = os.path.join(download_dir, filename) # Construct full file path
        total_size_in_bytes = int(response.headers.get('content-length', 0)) # Get file size from headers
        block_size = 1024 # 1KB blocks

        with open(file_path, 'wb') as pdf_file, tqdm(
            desc=filename,
            total=total_size_in_bytes,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar: # Use tqdm for progress bar
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk: # filter out keep-alive new chunks
                    progress_bar.update(len(chunk))
                    pdf_file.write(chunk)

        print(f"Successfully downloaded PDF to {file_path}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}") # More specific HTTP error message
        print(f"Status code: {response.status_code}") # Print status code for debugging
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as e: # Catch any other potential errors
        print(f"An unexpected error occurred: {e}")

def get_perplexity_search_results(query):
    api_key = os.environ.get("PERPLEXITY_API_KEY")

    if not api_key:
        print("PERPLEXITY_API_KEY not found in environment variables.")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant and you need to "
                "engage in a helpful, detailed, polite conversation with a user."
            ),
        },
        {   
            "role": "user",
            "content": (
                query
            ),
        },
    ]

    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

    # chat completion without streaming
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=messages,
    )

    message = response.choices[0].message.content + "\n\n"
    citations = response.citations

    for k, citation in enumerate(citations):
        message += f"[{k+1}] {citation}\n"
        #print(f"[{k+1}] {citation}")

    return message, citations

def get_google_search_results(query, num_results=10):
    api_key = os.environ.get("SERPER_API_KEY")

    if not api_key:
        print("SERPER_API_KEY not found in environment variables.")
        return

    url = "https://google.serper.dev/search"
    payload = json.dumps({
    "q": query,
    "num": num_results
    })
    headers = {
    'X-API-KEY': api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response

async def crawl_website_async(url_webpage, topic_folder_name):
    if is_pdf_url(url_webpage):
        download_pdf(url_webpage, filename="my_document.pdf", download_dir="./topic_folder_name", timeout=15)
        return None
        
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url_webpage,
        )
        return result.markdown

def crawl_website(url_webpage, topic_folder_name):
    return asyncio.run(crawl_website_async(url_webpage, topic_folder_name))

# Only run this block for Gemini Developer API
client = genai.Client()

flash_thinking_model = "gemini-2.0-flash-thinking-exp-01-21"
flash2_model = "gemini-2.0-flash-exp"
flash1_model = "gemini-1.5-flash"
model = GeminiModel(flash2_model)

class TableOfContentSection(BaseModel):
    main_chapter: str = Field(description="The main chapter or main sector.")
    sub_chapters: list[str] = Field(description="A list of subchapters linked to the main chapter.")
    citation_links: list[str] = Field(description="All the weblinks that are most suitable to write a report about this main chapter (including sub chapters). Only include links that contain processable text.")

class TableOfContentFullResponse(BaseModel):
    table_of_content: list[TableOfContentSection] = Field(description="The generated table of content for the scientific report/document. Each element in list contains a main chapter (incl. subchapters)")
    additional_notes: str = Field(description="If you want to add commentary based on things you've observed during the processing of the data you can add it here.")
    text_summary: str = Field(description="A one page summary of the given research topic based on the search results.")
    google_search_query: str = Field(description="The goole search query that was used to retrieve google web results.")
    perplexity_search_query: str = Field(description="The Perplexity search query that was used to retrieve web results.")

@dataclass
class ResearchDeps:
    research_topic: str = Field(description="The research topic of the document.")
    document_type: str = Field(description="The type of document for the table of content (paper/report/general document/webpage).")
    document_number_of_pages: int = Field(description="A rough estimate of how many pages the report will have. The table of content needs to reflect that.")



table_of_content_agent = Agent(
    model,
    deps_type=ResearchDeps,  
    result_type=TableOfContentFullResponse,
    system_prompt="""Your goal is to create the table of content for a scientific report based on given topic and given input text. 
    You don't need to generate the report (except the one page summary).
    Use all search tools available to you (only once) to collect information about the topic (don't exclude any).

    Use all tools to get an overview about the topic, then create the table of content for the report/paper/document.
    The table of content needs to contain the most interessting and important parts of the topic based on the desired page count of the report (more details for more report pages).
    """
)

@table_of_content_agent.system_prompt  
async def get_system_prompt(ctx: RunContext[ResearchDeps]) -> str:  
    context_string = f"Research Topic: {ctx.deps.research_topic}\n"
    context_string += f"Document Type: {ctx.deps.document_type}\n"
    context_string += f"Document Number of Pages: {ctx.deps.document_number_of_pages}\n"

    return context_string

@table_of_content_agent.tool_plain  
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

@table_of_content_agent.tool_plain  
def google_search(search_query: str, topic_folder_name: str) -> dict:
    """Uses the Serper API to retrieve google results based on a string query.
    Certain search results could be faulty or irrelevant, please ignore these results.

    Args:
        search_query (str): The google query string. It needs to be suited for the given research topic.
        topic_folder_name (str): A suitable name for a folder (all search results are saved in this folder). It needs to be a valid folder name.
    
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
    payload = json.dumps({
    "q": search_query,
    "num": num_results
    })
    headers = {
    'X-API-KEY': api_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_response = response.json()

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

    return document_data

async def run_agent(research_topic, document_type, document_number_of_pages):
    result = await table_of_content_agent.run('Write a table of content for a scientific report.', deps=ResearchDeps(research_topic=research_topic, document_type=document_type, document_number_of_pages=document_number_of_pages))
    return result

def write_document(result):
    text_summary = result.data.text_summary
    additional_notes = result.data.additional_notes

    main_chapter_number = 1
    sub_chapter_number = 1
    table_of_content = "" 
    chapter_links = []

    for item in result.data.table_of_content:
        main_chapter = item.main_chapter
        table_of_content = table_of_content + f"- {main_chapter_number}. {main_chapter}\n"
        chapter_links.append(item.citation_links)

        for sub_chapter in item.sub_chapters:
            table_of_content = table_of_content + f"    - {main_chapter_number}.{sub_chapter_number}. {sub_chapter}\n"
            sub_chapter_number += 1

        main_chapter_number += 1    
        sub_chapter_number = 1

    chapter_links_str = ""
    chapter_number = 1
    for chapter_link in chapter_links:
        chapter_links_str += f"- Chapter {chapter_number}:\n"
        for link in chapter_link:
            chapter_links_str += f"    - {link}\n"
        chapter_number += 1

    document_text = f"""Text Summary:
    {text_summary}

    Additional Notes:
    {additional_notes}

    Table of Content:
    {table_of_content}

    Chapter Links:
    {chapter_links_str}

    """

    # Save document to file
    with open("document.md", "w") as f:
        f.write(document_text)

if __name__ == "__main__":
    research_topic = "LLM Agents and the impact on the job market"
    document_type = "Scientific Report/Paper"
    document_number_of_pages = 10

    result = asyncio.run(run_agent(research_topic, document_type, document_number_of_pages))
    write_document(result)