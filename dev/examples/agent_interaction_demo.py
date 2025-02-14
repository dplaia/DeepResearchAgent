import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_tools import *
from agent_utils import *



if __name__ == "__main__":
    query = "How can human reasoning help store and retrieve contextualize knowledge?"
    response = openrouter_deepseekR1_call(query)
    # console_print(response.final_answer)
    new_query = f"""{query}

    Here are some of my previous notes and thoughts:
    {response.final_answer}
    """
    new_response = gemini_flash2_thinking_call(new_query)
    # console_print(new_response.final_answer)
    responseR1_2 = openrouter_deepseekR1_call(new_response.final_answer)
    console_print(responseR1_2.final_answer)
    new_response2 = gemini_flash2_thinking_call(responseR1_2.final_answer)
    console_print(new_response2.final_answer)
