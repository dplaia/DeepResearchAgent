import os
import time
from os.path import join, exists
from os import listdir, makedirs
from datetime import datetime
from google import genai
from google.genai import types
from openai import OpenAI
from openai import AsyncOpenAI
import requests
import json
from pydantic import BaseModel, Field
from crawl4ai import *
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
from queue import Queue, Empty
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Dict, Optional, List
import asyncio
import nest_asyncio 
# Add this line to allow nested event loops
nest_asyncio.apply()

from agent_tools import *
from agent_utils import *

from loguru import logger

config = Config()

console = Console()
# Log to a file with custom timestamp format
logger.add("chain_of_agent_output.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
model = GeminiModel(config.FLASH2_MODEL)

