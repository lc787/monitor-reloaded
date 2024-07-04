from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import requests
import json

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

type Status = str
type Id = str
type Rule = str
type InfraState = dict[Rule, list[dict[str, Id|Status]]] 
poll_result_parsed: InfraState = {}

# Templates
templates = Jinja2Templates(directory="templates")
poll_result_templated = None
"""
        for alertName,alerts in poll_result_parsed.items():
            print(f"\n\n {alertName}\n\n")
            for alert in alerts:
                for identifier,status in alert.items():
                    print(f"host:{identifier},status:{status}")
"""
async def poll_grafana(api_url: str, api_token: str) -> str:
    r = requests.get(api_url, headers={'Authorization': f'Bearer {api_token}'}, )
    if r.status_code != requests.codes.ok:
        print(f'Oops! Fucking failed. Error {r.status_code}')
        return None, r.status_code
    return r.json(), None


async def poll_task(sleep: Any):
    global total_polls, poll_result_parsed, poll_result_templated
    print(f'The new sleep is {sleep}')
    while True:
        start = time.time()
        res, err = await poll_grafana(api_url, api_token)
        poll_result_parsed = parse(res)
        print(json.dumps(poll_result_parsed))
        end = time.time()
        delta = max(0, end - start)
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
def parse(data: dict) -> InfraState:
    parsed: InfraState = {}
    rules = data["data"]["groups"][0]["rules"]
    for key in ["uptime", "proxmox", "aps", "temps"]:
        parsed[key] = []
    for rule in rules:
        alerts = rule["alerts"]
        alertname = rule["name"]
        # TODO: sort lists by id
        for alert in alerts:
            # parsed[numeRegulaALerta] => lista de dictionare
            # fiecare dictionar este o pereche de cheie valoare, key=Identifier(id,alias,etc...) Value=Status(normal/firing)
            match alertname:
                case "ping_exporter_rule":
                    parsed["uptime"].append({"id": alert["labels"]["alias"],
                                             "state": alert["state"]})
                case "proxmox_exporter_cpu":
                    parsed["proxmox"].append({"id": alert["labels"]["id"],
                                              "state":alert["state"]})
                case "snmp_rule":
                    parsed["aps"].append({"id": "AP"+alert["labels"]["mwApTableIndex"],
                                          "state": alert["state"]})
                # temperaturi
                case _ if alertname.startswith("temperature_alert_"):
                    parsed["temps"].append({"id": alertname[len("temperature_alert_"):],
                                            "state": alert["state"]})
    return parsed

def template_infra(request: Request, state: InfraState):
    return templates.TemplateResponse(
        request,
        "infra.html",
        context={
            "infra": poll_result_parsed,
        }
    )

# Webserver
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Routes
@app.put("/polling_interval")
async def update_polling_interval(new_interval: float) -> float:
    await change_polling_interval(new_interval)
    return new_interval

@app.get("/polling_interval")
def get_polling_interval() -> float:
    return polling_interval

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )

# The html view of the entire infrastructure
@app.get("/infra", response_class=HTMLResponse)
async def get_infra(request: Request):
    poll_result_templated = template_infra(request, poll_result_parsed)
    print(poll_result_templated)
    return poll_result_templated