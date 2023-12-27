import os
import json
import time
from openai import OpenAI
from tavily import TavilyClient
from colorama import Fore
from dotenv import load_dotenv
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
def wait_for_run_completion(thread_id, run_id):
    while True:
        time.sleep(1)
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
    # print(Fore.BLUE + messages.data[0].content[0].text.value)
    # for msg in messages:
    #     print(f"{msg.role}: {msg.content[0].text.value}")

# Create an assistant
# assistant = client.beta.assistants.create(
#     instructions=assistant_prompt_instruction,
#     # model="gpt-4-1106-preview",
#     model="gpt-3.5-turbo-1106",
#     tools=[{
#         "type": "function",
#         "function": {
#             "name": "tavily_search",
#             "description": "Get information on recent events from the web.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "query": {"type": "string", "description": "The search query to use. For example: 'Latest news on Nvidia stock performance'"},
#                 },
#                 "required": ["query"]
#             }
#         }
#     },
#     # {"type": "code_interpreter"}
#     ]
# )
# assistant_id = "asst_pnlBriOnH1QKrcT6yigalxJW"
# thread_id ="thread_jiZvg8hZkBUwhPK2OBxmssxk"

# assistant_id = "asst_4J2PUh36zMLWDlSJzv2i9fTe"
# thread_id ="thread_ovXPaL58Kr6K75UQP0HtFNvx"
#mine google
# assistant_id = "asst_FCV0DSNf4HYrOkjS0CEV9vii"
# thread_id ="thread_YpwT5YGHVfuVxRfm9kYus6jk"
#mine no google
assistant_id = "asst_JzCfsVN7iXX7yjqomPagnwWk"
thread_id ="thread_mOtvBHFRAKZLZ1fhi5qFkz8l"
# print(Fore.LIGHTGREEN_EX+f"Assistant ID: {assistant_id}")

# # Create a thread
# thread = client.beta.threads.create()
# print(Fore.LIGHTGREEN_EX+f"Thread: {thread}")

# Ongoing conversation loop


def ai_response(message):
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
        run = wait_for_run_completion(thread_id, run.id)

        if run.status == 'failed':
            print(Fore.LIGHTGREEN_EX+run.error)
            continue
        elif run.status == 'requires_action':
            run = submit_tool_outputs(thread_id, run.id, run.required_action.submit_tool_outputs.tool_calls)
            run = wait_for_run_completion(thread_id, run.id)

        # Print messages from the thread
        res = print_messages_from_thread(thread_id)
        return res