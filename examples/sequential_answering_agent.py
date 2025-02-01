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
from dataclasses import dataclass
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
from queue import Queue, Empty
import asyncio

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_tools import *
from agent_utils import *

from loguru import logger

config = Config()

console = Console()

# Log to a file with custom timestamp format
logger.add("agent_output.log", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
model = GeminiModel(config.FLASH2_MODEL)


class Answer(BaseModel):
   
    answer: str = Field(description="The answer for the question (if available).")
    notes: list[str] = Field(description="Add study notes or pieces of text that helps other assistants to answer the question in the future. The better the quality of the notes, the more likely it is to get better responses in the future.")
    index: int = Field(description="Equals question number or index.")
    rating: int = Field(description="Rate the quality of your response between 0 and 10", ge=0, le=10)

class Question(BaseModel):
    question: str = Field(description="The question that needs to be answered.")
    index: int = Field(description="The question number or index.")

class Deps(BaseModel):
    questions: dict[int, Question] = Field(description="A dict with questions that need to be answered (keys: question number, values: question).")

    def get_all_questions(self) -> dict:
        return self.questions

    def remove_question(self, idx: int) -> bool:
        if idx not in self.questions.keys():
            return False

        del self.questions[idx]
        
        return True

async def run_againt():
    questions_list = [
        "Explain the concept of 'artificial intelligence' in a way that a 10-year-old could understand.", 
        "Compare and contrast the philosophies of Plato and Aristotle, highlighting their key differences and similarities in their views on ethics and knowledge.", 
        "Write a short poem about the feeling of walking through a forest in autumn.",
        "If someone is planning a trip to Italy and enjoys art and history, what are three cities you would recommend they visit and why?",
        "Summarize the main arguments for and against universal basic income."]

    question_dict = {}
    for (k,q) in enumerate(questions_list):
        question = Question(question=q, index=k)
        question_dict[k] = question

    deps = Deps(questions=question_dict)

    system_prompt="""
    You are a helpful assistant.

    - First get all questions (use tools)
    - Then, choose only one question
    - Finally answer the one question
    """

    agent = Agent(
        model,
        deps_type=deps,  
        result_type=Answer,
        system_prompt=system_prompt)

    @agent.tool
    def get_all_questions(ctx: RunContext[Deps]) -> dict:
        return ctx.deps.get_all_questions()

    saved_answered = []

    for k in range(5):
        
        result = await agent.run('Get all questions and give an answer to only one question.', deps=deps)
        console.print(Markdown(result.data.answer))
        logger.info(f"LLM Output: {result.data.answer}")

        saved_answered.append(result.data)

        if result.data.rating >= 8:
            # remove question from deps
            deps.remove_question(result.data.index)

        time.sleep(1)


if __name__ == "__main__":

    result = asyncio.run(run_agent())
