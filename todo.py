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


# @app.post("/add-task")
# async def create_task(request: Request):
#     signals = await read_signals(request)
#     try:
#         title = signals["new_task"]
#         new_task = data.create_task_obj(title)
#         data.tasks.append(new_task)
#     except Exception as e:
#         print("EXCEPTION:", e)
#     context = {"tasks": data.tasks}
#     return templates.TemplateResponse(
#         request=request, name="index.html", context=context
#     )

task_list_html = """

  <div 
    class="task-element" 
    id={task_id} 
    data-on:click="$clickedTask=el.id; 
        @post('/mark-completed')">{task_name} ->
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

    print(whole_element_html)

    async def _():
        yield SSE.patch_elements(whole_element_html)
        yield SSE.patch_signals({"new_task":""})

    return _()


@app.post("/delete-all-tasks")
async def delete_all_tasks(request: Request):
    data.tasks.clear()
    context = {"tasks": data.tasks, "status": "all tasks deleted"}
    return templates.TemplateResponse(
        request=request, name="index.html", context=context
    )


@app.post("/mark-completed")
async def mark_completed(request: Request):
    signals = await read_signals(request)
    print(signals)
    clicked_task = signals["clickedTask"]
    print("clicked_task", clicked_task)
