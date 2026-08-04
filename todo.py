import asyncio
import json

import datastar_py.fastapi as dsfapi
from datastar_py import ServerSentEventGenerator as SSE
from datastar_py.fastapi import (
    DatastarResponse,  # noqa: F401
    datastar_response,
    read_signals,  # noqa: F401
)
from fastapi import FastAPI, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import data

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
@app.get("/home")
def home(request: Request):
    context = {"tasks": data.tasks}
    return templates.TemplateResponse(
        request=request, name="index.html", context=context
    )


@app.post("/add-task")
async def create_task(request: Request):
    signals = await read_signals(request)
    try:
        data.tasks.append(signals["new_task"])
    except Exception as e:
        print("EXCEPTION:", e)
    context = {"tasks": data.tasks}
    return templates.TemplateResponse(
        request=request, name="index.html", context=context
    )



@app.post("/delete-all-tasks")
async def delete_all_tasks(request: Request):
    data.tasks.clear()
    context = {"tasks": data.tasks, "status": "all tasks deleted"}
    return templates.TemplateResponse(
        request=request, name="index.html", context=context
    )

