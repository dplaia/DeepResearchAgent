sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_utils import *
from agent_tools import *
import argparse

config = Config()

# Log to a file with custom timestamp format
logger.add("logs/chain_of_thougth_agent_system.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
model = GeminiModel(config.FLASH2_MODEL)

reasoningAgentChat = ChatHandler()

basicSearchAgent = BasicSearchAgent(perplexity_search=False)

class SearchQueryAgentResponse(BaseModel):
    google_search_queries: list[str] | None = Field(description="The extracted google search queries (if available).")
    google_scholar_queries: list[str] | None = Field(description="The extracted google scholar queries (if available).")
    text_summary: str  | None = Field(description="Extract the text summary here (if available).")

searchQueryAgent = BaseAgent(SearchQueryAgentResponse, 
        system_prompt="""Your goal is to extract search queries (e.g., google search, google scholar, etc.) 
        that are mention in a text.""")

class URLRating(BaseModel):
    url_number: int = Field(description="The URL number", ge=0)
    rating: int = Field(description="The rating (value between 0 and 100) for the URL", ge=0, le=100)

class URLRatingAgentResponse(BaseModel):
    url_info: list[URLRating] = Field(description="A list with URLs with corresponding ratings.")

urlRatingAgent = BaseAgent(URLRatingAgentResponse, 
        system_prompt="""Your goal is to extract URL number and the corresponding rating. 
        The input text has the following format: {1, 60}, {2,75}, {3, 35} .... 
        with  
        {URL number, Rating}""")

def get_document():
    documents = {}
    folder_name = 'input_files/'

    # Create directory if it doesn't exist
    if not exists(folder_name):
        makedirs(folder_name, exist_ok=True)

    main_input_file = join(folder_name, "Vorhabenbeschreibung_NeuroTrust.txt")

    if not exists(main_input_file):
        print("file does not exists")
        # Process each file in the input directory
        for filename in listdir(folder_name):
            filepath = join(folder_name, filename)
            
            if not os.path.isfile(filepath):
                continue
                
            try:
                md = MarkItDown()
                result = md.convert(filepath)
                filename = os.path.basename(filepath)
                documents[filename] = result.text_content
            except Exception as e:
                print(f"Error processing {filepath}: {str(e)}")
                continue

        doc = ""
        for filename in documents:
            print(f"Filename: {filename}")
            doc = documents[filename]
            count = word_count(doc)
            print(f"Number of Words in the document: {count}")

            break

        with open(main_input_file, "w", encoding="utf-8") as f:
            f.write(doc)

    else:
        with open(main_input_file, "r", encoding="utf-8") as f:
            doc = f.read()

    return doc

async def get_search_queries_for_document(doc: str):
    query = get_system_prompt("search_query_recommendation")
    query += f"""
    # Input Document: 

    {doc}
    """
    
    text_response = await reasoningAgentChat(query)
    queries = await searchQueryAgent(f"Please extract all search queries from this text: {text_response}")

    return queries.data

async def get_search_query_help(query: str):

    query += f"""
    We have to improve the search results given a user search query. 
    Please think of multiple google search queries (plain text) that would increase the quality of the search results, when we combine all the search results.

    # Desired output format:

    Google Search Queries:
    - Search query 1
    - Search query 2
    - etc.

    # User Search Query:
    {query}

    """
    
    text_response = await reasoningAgentChat(query)
    queries = await searchQueryAgent(f"Please extract all search queries from this text: {text_response}")

    return queries.data

async def rate_search_results(content_text: str):
    query = f"""
    Please rate each search result based on relevance (value between 0 and 100).
    Each search result has an URL with an URL number, 
    for example: "Link [143]: https...", where 143 is the URL number.

    Your generated output format should look like this:

    (1, 60), (2,75), (3, 35) ....
    
    with 
    
    (URL number, Rating)  
    
    Here are the search results based on your search query suggestions:
    
    {content_text}
    """
    text_response = await reasoningAgent(query)

    url_info = await urlRatingAgent(f"Please extract the url info in this text: {text_response}")

    return url_info.data

async def search_queries(search_queries: list[str]) -> list[str]:
    results = []
    for query in search_queries:
        print(f"Search query: {query}")
        response = await basicSearchAgent(query)
        results.append(response)
    return results

async def generate_research_report(user_search_query, result_text) -> str:
    response = await reasoningAgentChat(f"""
        Please generate a high quality report text based on the search results (output in Markdown format).
        Add a reference section with citations at the end. Use the urls that are present in the input text, don't use other urls.
        Format:
        # References
        [1] http...
        [2] etc.

        Add the correct citations in the writen report. 

        The text should be as relevant to the user search query as possible. 

        # User Search Query:
        {user_search_query} 

        #Search Results (text):
        {result_text}
        
        """)

    return response


async def run_search(user_search_query: str, max_searches:int = 5, use_perplexity: bool=False) -> None:
    global basicSearchAgent
    basicSearchAgent = BasicSearchAgent(perplexity_search=use_perplexity)

    queries = await get_search_query_help(user_search_query)
    results = await search_queries(queries.google_search_queries[:max_searches])

    result_text = ""

    for k, result in enumerate(results):
        #console_print(result)
        result_text += f"""
        # Result query {k+1}:

        {result}

        """

    response = await generate_research_report(user_search_query, result_text)
    return response

async def main():
    parser = argparse.ArgumentParser(description="Run extended web searches.")
    parser.add_argument("user_search_query", type=str, help="The initial search query.")
    parser.add_argument("-m", "--max_searches", type=int, default=5, help="Maximum number of searches to perform.")
    parser.add_argument("-p", "--use_perplexity", action="store_true", help="Enable perplexity for search expansion.")

    args = parser.parse_args()

    report_text = await run_search(args.user_search_query, args.max_searches, args.use_perplexity)
    console_print(report_text)


if __name__ == "__main__":
    asyncio.run(main())