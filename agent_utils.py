import re
import asyncio
import requests
from collections import deque
from functools import wraps
import time
import threading

from config import Config

config = Config()

_rate_limit_registry = {}
_registry_lock = threading.Lock()

def rate_limit(name: str, rpm: int = 10):
    """Decorator to enforce RPM limits for function groups"""
    with _registry_lock:
        if name not in _rate_limit_registry:
            _rate_limit_registry[name] = {
                'timestamps': deque(maxlen=rpm),
                'lock': threading.Lock(),
                'window': 60.0
            }

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            group = _rate_limit_registry[name]
            with group['lock']:
                now = time.time()
                
                if len(group['timestamps']) >= rpm:
                    oldest = group['timestamps'][0]
                    elapsed = now - oldest
                    
                    if elapsed < group['window']:
                        sleep_time = group['window'] - elapsed
                        time.sleep(sleep_time)
                        now = time.time()
                
                group['timestamps'].append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

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