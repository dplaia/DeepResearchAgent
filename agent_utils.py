import asyncio
import requests
from crawl4ai import AsyncWebCrawler
from markitdown import MarkItDown
from config import Config

config = Config()


def is_pdf_url(url: str, timeout: int = config.REQUEST_TIMEOUT) -> bool:
    """
    Determines if a URL points to a PDF document
    
    Args:
        url: Web address to check
        timeout: Request timeout in seconds
        
    Returns:
        True if content is PDF, False otherwise
        
    Raises:
        ValueError: For invalid URL format
    """
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL format")
        
    try:
        # Try HEAD first to avoid downloading content
        response = requests.head(url, allow_redirects=True, timeout=timeout)

        # Fallback to GET if HEAD not allowed
        if response.status_code == 405:
            response = requests.get(url, stream=True, timeout=timeout)

        content_type = response.headers.get('Content-Type', '').lower()
        return 'application/pdf' in content_type

    except RequestException as e:
        print(f"Error checking PDF URL: {str(e)}")
        return False
