from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, PlainTextResponse
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
        "text": "thinking...."
    }
    payload_json = json.dumps(payload)
    response = requests.post(url, data=payload_json, timeout=120)

    payload = {
        "text": await ai_response(msg) + msg
    }
    payload_json = json.dumps(payload)

    # Send a POST request to the response_url with the payload
    response = requests.post(url, data=payload_json, timeout=120)


@app.post("/api/ai_response", response_class=PlainTextResponse)
async def verify_hook(req: Request, background_tasks: BackgroundTasks):
    s =await req.body()
    s= urllib.parse.unquote(s)
    d = urllib.parse.parse_qs(s)
    d = {k: v[0] for k, v in d.items()}
    print(d)
    response_url = d["response_url"]
    background_tasks.add_task(send_second_res, response_url, d["text"])
    