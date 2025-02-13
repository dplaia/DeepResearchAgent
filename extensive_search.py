import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import controlflow as cf

from agent_utils import *
from agent_tools import *
import argparse

reasoningAgentChat = ReasoningModel()
basicSearchAgent = BasicSearchModel(perplexity_search=False)

def ask_reasoning_model(content: str) -> str:
    global reasoningAgentChat

    response = reasoningAgentChat(content)
    return response

def google_single_search(search_query: str) -> str:
    global basicSearchAgent
    result_text = basicSearchAgent(search_query)
    return result_text

def google_search(search_queries: list[str]) -> list[str]:
    results = []
    for query in search_queries:
        print(f"Search query: {query}")
        response = google_single_search(query)
        results.append(response)
    return results

def search_query_help(search_query: str) -> str:
    query = f"""
    We have to improve the search results given a user search query. 
    Please think of multiple google search queries (plain text) that would increase the quality of the search results, when we combine all the search results.

    # Desired output format:

    Google Search Queries:
    - Search query 1
    - Search query 2
    - etc.

    Please sort the queries based on relevance/impact. First queries (Search query 1,2,3) are more relevant than last.

    # User Search Query:
    {search_query}

    """
    
    text_response = reasoningAgentChat(query)
    return text_response

class SearchQueryAgentResponse(BaseModel):
    google_search_queries: list[str] = Field(description="The extracted google search queries (if available).")
    # google_scholar_queries: list[str] | None = Field(description="The extracted google scholar queries (if available).")
    # text_summary: str  | None = Field(description="Extract the text summary here (if available).")

searchQueryAgent = cf.Agent(
    name="Query",
    model = "google/gemini-2.0-flash",
    instructions=f"""
    Your goal is to extract search queries (e.g., google search, google scholar, etc.) that are mention in a text.
    """
)

def generate_research_report(user_search_query, result_text) -> str:
    global reasoningAgentChat

    response = reasoningAgentChat(f"""
        Please generate a high quality report text based on the search results.
        
        The output should be in Markdown format, but please don't wrap the text like this:
        ```markdown
        # The report
        ```

        Add the correct citations in the writen report in the following style:
        "... outage caused disruption to online gaming and affected the stock market [1]. "

        Add a reference section with citations at the end. Use the urls that are present in the input text, don't use other urls.

        Format:

        # References

        [1] [thehindu.com](https://...) # always add two spaces at the end -> "  "
        [2] [google.com](https://...)
        [3] [indianexpress.com](https://...)
        [4] [hindustantimes.com](https://...)
        [5] [aljazeera.com](https://...)
        [6] etc. 

        The text should be as relevant to the user search query as possible. The lenght of the report should depend on the amound of sources available to you and based on the user query. 
        More sources with more diverse information (and more user questions) means longer report.
        The language report depends on the user query. If the user query is in English, write the report only in English. If the user query is in German, write the report only in German, etc. 

        # User Search Query:
        {user_search_query} 

        #Search Results (text):
        {result_text}


        """)    

    return response

def get_search_result_text(results: list[str]) -> str:
    result_text = ""
    for k, result in enumerate(results):
        #console_print(result)
        result_text += f"""
        # Result query {k+1}:

        {result}

        """
    return result_text

def run_research(search_query: str, max_searches: int = 10) -> str:
    search_queries_text = search_query_help(search_query)
    console_print(search_queries_text)

    task_extract_search_queries = cf.Task(
        objective=f"Extract all search queries from the input text",
        instructions=f"Extract the google search and google scholar search queries from the text. Here is the input text:  {search_queries_text}",
        result_type=SearchQueryAgentResponse,
        agents=[searchQueryAgent]
    )

    result = task_extract_search_queries.run()
    results = google_search(result.google_search_queries[:max_searches])
    result_text = get_search_result_text(results)

    print("Writing report now ...")
    response = generate_research_report(search_query, result_text)
    
    return response


def main():

    parser = argparse.ArgumentParser(description="Run extended web searches.")
    parser.add_argument("query", type=str, help="The initial search query.")
    parser.add_argument("-m", "--max_searches", type=int, default=5, help="Maximum number of searches to perform.")
    parser.add_argument("-s", "--save", action="store_true", help="Save the report as markdown file.")
    #parser.add_argument("-p", "--use_perplexity", action="store_true", help="Enable perplexity for search expansion.")

    args = parser.parse_args()

    report_text = run_research(args.query, args.max_searches)

    if args.save:
        with open("markdown_output.md", "w") as f:
            f.write(report_text)

    console_print(report_text)


if __name__ == "__main__":
    main()