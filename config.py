from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Final

class Config(BaseSettings):
    """Global configuration settings"""
    MAX_RETRIES: int = Field(default=3)
    REQUEST_TIMEOUT: int = Field(default=10)
    CRAWL_CONCURRENCY: int = Field(default=5)
    PAPERS_PER_PAGE: int = Field(default=200)
    
    # API endpoints
    PERPLEXITY_BASE_URL: str = Field(default="https://api.perplexity.ai")
    SERPER_BASE_URL: str = Field(default="https://google.serper.dev/search")

    # API Keys
    SERPER_API_KEY: str = Field(..., env="SERPER_API_KEY")
    PAPERS_WITH_CODE_CSRF_TOKEN: str = Field(default="2ix1PR0FtUWIW5ePo08I3vhgHsvJ6fpqj0x1Ijjo4egxiofnUBzkX67bnHwbNd8G")
    PERPLEXITY_API_KEY: str = Field(..., env="PERPLEXITY_API_KEY")
    
    # Tool Descriptions
    TOOL_DESCRIPTIONS: Final = {
        "google_general": "General web search using Google via Serper API",
        "scholar": "Academic search using Google Scholar",
        "perplexity": "LLM-powered search with Perplexity AI",
        "papers_with_code": "Research paper search with code implementations"
    }
    
    # Model Settings
    FLASH1_MODEL: str = Field(default="gemini-1.5-flash")
    FLASH2_MODEL: str = Field(default="gemini-2.0-flash-exp")
    
    class Config:
        env_file = ".env"
        extra = "ignore"
