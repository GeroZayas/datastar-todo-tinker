""" 
To-do:
a) when click on task - open subtasks
b) add button to edit and delete 
c) 

"""

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
from rich import print

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

task_list_html = """

  <div 
    style="display: flex;"
    class="task-element" 
    id={task_id} 
    data-on:click="$clickedTask=el.id; 
        @post('/mark-completed')">
        <div class="check-btn"></div>
        {task_name} ->
        <span>{task_completed}</span>
  </div>
  <br>
"""


@app.post("/add-task")
@datastar_response
async def create_task(request: Request):
    signals = await read_signals(request)
    print(signals)
    title = signals["new_task"]
    new_task = data.create_task_obj(title)
    data.tasks.append(new_task)

    print(data.tasks)

    whole_element_html = """<div id="task-list-2" class="task-list">"""

    for t in data.tasks:
        element_to_patch = task_list_html.format(
            task_id=t.id,
            task_name=t.name,
            task_completed=t.completed,
        )
        whole_element_html += element_to_patch
    
    whole_element_html += """</div>"""

    # print(whole_element_html)

    async def _():
        yield SSE.patch_elements(whole_element_html)
        yield SSE.patch_signals({"new_task":""})

    return _()

delete_tasks_html = """<div id="task-list-2" class="task-list"></div>"""

@app.post("/delete-all-tasks")
@datastar_response
async def delete_all_tasks(request: Request):
    data.tasks.clear()
    async def _():
        yield SSE.patch_elements(delete_tasks_html)
    return _()
    

@app.post("/mark-completed")
async def mark_completed(request: Request):
    signals = await read_signals(request)
    print(signals)
    clicked_task = signals["clickedTask"]
    print("clicked_task", clicked_task)
