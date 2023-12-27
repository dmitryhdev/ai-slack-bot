import os
import json
import time
from openai import OpenAI
from tavily import TavilyClient
from colorama import Fore
from dotenv import load_dotenv
import asyncio
load_dotenv()
# Initialize clients with API keys
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])



assistant_prompt_instruction = """You are a AI expert. 
Don't search web. Response with your current knowledge.
"""

# Function to perform a Tavily search
def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    print(Fore.LIGHTGREEN_EX+search_result)
    return search_result

# Function to wait for a run to complete
async def wait_for_run_completion(thread_id, run_id):
    while True:
        asyncio.sleep(0.2)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(Fore.LIGHTGREEN_EX+f"Current run status: {run.status}")
        if run.status in ['completed', 'failed', 'requires_action']:
            return run

# Function to handle tool output submission
def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = tool.function.arguments

        if function_name == "tavily_search":
            output = tavily_search(query=json.loads(function_args)["query"])

        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )

# Function to print messages from a thread
def print_messages_from_thread(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value

assistant_id = os.environ["ASSISTANT_ID"]
thread_id =os.environ["THREAD_ID"]



async def ai_response(message):
    user_input = message
    
    while True:
        # Create a message
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input,
        )

        # Create a run
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        print(Fore.LIGHTGREEN_EX+f"Run ID: {run.id}")

        # Wait for run to complete
        run = await wait_for_run_completion(thread_id, run.id)

        if run.status == 'failed':
            print(Fore.LIGHTGREEN_EX+run.error)
            continue
        elif run.status == 'requires_action':
            run = submit_tool_outputs(thread_id, run.id, run.required_action.submit_tool_outputs.tool_calls)
            run = await wait_for_run_completion(thread_id, run.id)

        # Print messages from the thread
        res = print_messages_from_thread(thread_id)
        return res