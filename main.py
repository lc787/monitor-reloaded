from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import requests

import re
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
        print("am intrat")
        start = time.time()
        res, err = await poll_grafana(api_url, api_token)
        parse(res)
        print("am scapat!")
        end = time.time()
        delta = max(0, end-start)
        total_polls += 1
        if err != None:
            print(f'Epic fail. Error code: {err}')
        else:
            print(f'Total requests: {total_polls}')
        await asyncio.sleep(sleep - delta)

async def stop_polling():
    global poll_task_handle
    poll_task_handle.cancel()
    try:
        await poll_task_handle
    except asyncio.CancelledError:
        pass

async def start_polling(interval: float):
    global poll_task_handle
    # Point of failure: don't start a new task unless the other one is finished
    # otherwise, stop it
    if poll_task_handle != None and not poll_task_handle.cancelled():
        await stop_polling()
    poll_task_handle = asyncio.create_task(poll_task(interval))

async def change_polling_interval(new_interval: float):
    global polling_interval
    await stop_polling()
    polling_interval = new_interval
    await start_polling(new_interval)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global poll_task_handle
    await start_polling(polling_interval)
    yield
# JSON PARSING
def parse(jsonData:dict):

    rules = jsonData["data"]["groups"][0]["rules"]
    for rule in rules:
        alerts = rule["alerts"]
        i = 0;
        
        for alert in alerts:
            alertname = alert["labels"]["alertname"]
            match alertname:
                case "ping_exporter_rule":
                    print(f"{alert["labels"]["alias"]}:{alert["state"]}")
                case "proxmox_exporter_cpu":
                    print(f"{alert["labels"]["id"]}:{alert["state"]}")
                case "snmp_rule":
                    print(f"AP:{alert["labels"]["mwApTableIndex"]}:{alert["state"]}")
                # temperaturi
                case _ if alertname.startswith("temperature_alert"):
                    print(f"{alertname}:{alert["state"]}")
# Webserver
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routes
@app.put("/polling_interval")
async def update_polling_interval(new_interval: float):
    await change_polling_interval(new_interval)
    return new_interval

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(
        name="index.html", context={"request": request}
        )
