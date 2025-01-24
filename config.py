from typing import Final

class Config:
    """Global configuration settings"""
    MAX_RETRIES: Final[int] = 3
    REQUEST_TIMEOUT: Final[int] = 10
    CRAWL_CONCURRENCY: Final[int] = 5
    
    # API endpoints
    PERPLEXITY_BASE_URL: Final[str] = "https://api.perplexity.ai"
    SERPER_BASE_URL: Final[str] = "https://google.serper.dev/search"
