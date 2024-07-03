from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import requests

import asyncio
import time
from typing import Any
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from os import getenv

# Env
load_dotenv()
api_url = getenv("API_URL")
api_token = getenv("API_TOKEN")

# Server-wide polling
polling_interval: float = 5.0
poll_result = None
poll_task_handle: asyncio.Task = None
total_polls = 0

async def poll_grafana(api_url: str, api_token: str) -> str:
    r = requests.get(api_url, headers={'Authorization': f'Bearer {api_token}'}, )
    if r.status_code != requests.codes.ok:
        print(f'Oops! Fucking failed. Error {r.status_code}')
        return None, r.status_code
    return r.json(), None

async def poll_task(sleep: Any):
    global total_polls
    print(f'The new sleep is {sleep}')
    while True:
        start = time.time()
        res, err = await poll_grafana(api_url, api_token)
        end = time.time()
        delta = max(0, end-start)
        total_polls += 1
        if err != None:
            print(f'Epic fail. Error code: {err}')
        else:
            print(f'Total requests: {total_polls}')
        await asyncio.sleep(sleep - delta)
        
async def change_polling_interval(new_interval: float):
    global poll_task_handle, polling_interval
    poll_task_handle.cancel()
    polling_interval = new_interval
    poll_task_handle = asyncio.create_task(poll_task(new_interval))

@asynccontextmanager
async def lifespan(app: FastAPI):
    global poll_task_handle
    poll_task_handle = asyncio.create_task(poll_task(polling_interval))
    yield

# Webserver
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# Routes
@app.put("/polling_interval")
async def update_polling_interval(new_interval: float):
    await change_polling_interval(new_interval)
    return new_interval



