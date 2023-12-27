from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, PlainTextResponse
# from fastapi_slack import SlashCommand, router
# from freshbooks import Client
# from api.setup import setup_controller
# from api.schema import WebhookVerify
# from api.verifycode import verify_controller, webhook_verify
# from api.config import settings
from api.controllers.ai_slackbot import ai_response
import urllib.parse
from urllib.parse import parse_qs
from api.models.slack import SlackMessage
import requests
import time
import json
import asyncio


app = FastAPI(timeout=120)

async def send_second_res(url, msg):
    payload = {
        "text": ai_response(msg) + msg
    }
    # await asyncio.sleep(2)
    # Convert the payload to JSON format
    payload_json = json.dumps(payload)

    # Send a POST request to the response_url with the payload
    response = requests.post(url, data=payload_json, timeout=120)


@app.post("/api/ai_response", response_class=PlainTextResponse)
# async def verify_hook(slash_command: SlashCommand = Depends()):
async def verify_hook(req: Request, background_tasks: BackgroundTasks):
    s =await req.body()
    s= urllib.parse.unquote(s)
    d = urllib.parse.parse_qs(s)
    d = {k: v[0] for k, v in d.items()}
    print(d)
    response_url = d["response_url"]
    background_tasks.add_task(send_second_res, response_url, d["text"])
    return "thinking..." + d["text"]
    
    # data = parse_qs(req.body())
    # text = message.text
    # return  ai_response(d["text"])
    # return d["text"]


# import requests

# freshBooksClient = Client(
#     client_id="71f8d9e091f36ac5e40b8939b4793da813c3df51b45735271bb380ede4e903d9",
#     client_secret="cc2bc7903a859510616d0582d60d4d8d6e86dffdc21838b9a39a20f1df559c10",
#     redirect_uri="https://nextjs-fastapi-starter-bay-seven.vercel.app/"
# )

# authorization_url = freshBooksClient.get_auth_request_url(
#     scopes=['user:profile:read', 'user:projects:read']
# )
# print(f"Go to this URL to authorize: {authorization_url}")
# token_response = freshBooksClient.get_access_token("528902786626d712291a8c2aabde6fbbd1bbfb451d2e95a6efaaafff9fd281fe")
# print(token_response)


# # Define your FreshBooks API token and base URL
# token = "d1f7dde5535261316bc53570e3d02db06cbb0821c8c2814f9cb884beaa4382fb"
# base_url = "https://api.freshbooks.com"

# # Define the headers for authorization and content type
# headers = {
#     "Authorization": f"Bearer {token}",
#     "Content-Type": "application/json"
# }

# # Define the endpoint for getting a single project
# endpoint = f"/projects/business/<business_id>/project/11763941"

# # Make a GET request to the endpoint and store the response
# response = requests.get(base_url + endpoint, headers=headers)
# print(response)
# # Check if the response status code is 200 (OK)
# if response.status_code == 200:
#     # Parse the response as JSON and get the project data
#     data = response.json()
#     project = data["response"]["result"]["project"]

#     # Get the project name, budget amount, and spent amount
#     name = project["title"]
#     budget = project["budget"]["amount"]
#     spent = project["budget"]["spent"]

#     # Calculate the percentage of completion using the cost-to-cost method
#     # This method compares the spent amount to the budget amount
#     # Source: Percentage of Completion Method Decoded - FreshBooks [^1^]
#     percentage = round((spent / budget) * 100, 2)

#     # Print the project name and the percentage of completion
#     print(f"The project '{name}' is {percentage}% completed.")
# else:
#     # Print an error message if the response status code is not 200 (OK)
#     print(f"An error occurred: {response.status_code}")

#     print(freshBooksClient)
# @app.get("/api/python", response_class=HTMLResponse)
# def hello_world():
#     return "<html><button>ddd123 {}</button></html>".format(settings.redis_db)

# @app.get("/api/set-up", response_class=HTMLResponse)
# def set_up():
#     return setup_controller()


# @app.get("/api/verify", response_class=HTMLResponse)
# def verify(code: str):
#     return verify_controller(code)


# @app.post("/api/webhook", response_class=HTMLResponse)
# async def verify_hook(req: Request):
#     return await webhook_verify(req)


