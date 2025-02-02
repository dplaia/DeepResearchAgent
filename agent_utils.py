import re
import asyncio
import requests
from collections import deque
from functools import wraps
import time
import threading
import os
from os.path import join
from config import Config
from typing import Dict, Optional, List
from rich.console import Console
from rich.markdown import Markdown
console = Console()

config = Config()


def console_print(text: str, markdown: bool = True):
    if markdown:
        console.print(Markdown(text))
    else:
        console.print(text)

class RateLimiter:
    def __init__(self, rpm: int = 10, window: float = 60.0):
        self.rpm = rpm
        self.window = window
        self.timestamps = deque(maxlen=rpm)
        self.lock = threading.Lock()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()
                if len(self.timestamps) >= self.rpm:
                    oldest = self.timestamps[0]
                    elapsed = now - oldest
                    if elapsed < self.window:
                        sleep_time = self.window - elapsed
                        time.sleep(sleep_time)
                        now = time.time()
                self.timestamps.append(now)
            return func(*args, **kwargs)
        return wrapper

def apply_rate_limit(functions, agent_name, rpm_value):
    rate_limiter = RateLimiter(rpm=rpm_value) # Create a rate limiter instance
    return [rate_limiter(func) for func in functions]

def read_system_prompt(name: str) -> Optional[str]:
    if not name.endswith(".txt"):
        name = f"{name}.txt"

    directory = 'system_prompts'
    filepath = join(directory, name)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            prompt = f.read()
        return prompt
    else:
        print(f"File {name} does not exists in folder {directory}.")
    return None

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
# Pre-compile pattern for better performance
WORD_PATTERN = re.compile(r"(?<!\w)'|'(?!\w)", re.UNICODE)

def word_count(text: str) -> int:
    """Count words in text using more robust word matching.
    
    Handles:
    - Contractions (don't → 1 word)
    - Hyphenated words (state-of-the-art → 1 word)
    - Apostrophes in quotes ("rock 'n' roll" → 3 words)
    """
    if not text.strip():
        return 0

    # Normalize apostrophes and hyphens
    text = WORD_PATTERN.sub('', text.replace('-', ' '))
    return len(re.findall(r"[\w']+", text))

def test_word_count():
    # Basic cases
    assert word_count("hello world") == 2
    assert word_count("Don't panic!") == 2  # Contraction
    
    # Edge cases
    assert word_count("state-of-the-art") == 1  # Hyphenated
    assert word_count("hello_world") == 1  # Underscores
    assert word_count("") == 0  # Empty string
    assert word_count("   ") == 0  # Whitespace
    
    # Punctuation handling
    assert word_count("Hello, world!") == 2
    assert word_count("Rock 'n' roll") == 3  # Apostrophes in quotes