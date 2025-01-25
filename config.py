import os
from typing import Final

class Config:
    """Global configuration settings"""
    MAX_RETRIES: Final[int] = 3
    REQUEST_TIMEOUT: Final[int] = 10
    CRAWL_CONCURRENCY: Final[int] = 5
    PAPERS_PER_PAGE: Final[int] = 200
    
    # API endpoints
    PERPLEXITY_BASE_URL: Final[str] = "https://api.perplexity.ai"
    SERPER_BASE_URL: Final[str] = "https://google.serper.dev/search"
    
    # API Keys
    SERPER_API_KEY: Final[str] = os.environ.get("SERPER_API_KEY", "")
    PAPERS_WITH_CODE_CSRF_TOKEN: Final[str] = "2ix1PR0FtUWIW5ePo08I3vhgHsvJ6fpqj0x1Ijjo4egxiofnUBzkX67bnHwbNd8G"
    PERPLEXITY_API_KEY: Final[str] = os.environ.get("PERPLEXITY_API_KEY", "")
    
    # Model Settings
    FLASH1_MODEL: Final[str] = "gemini-1.5-flash"
    FLASH2_MODEL: Final[str] = "gemini-2.0-flash-exp"
