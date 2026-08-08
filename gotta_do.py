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
from datastar_py import consts
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
from icecream import ic
from rich import print

import data

# Useful
# -------

stop = lambda: input(".. hit ENTER to continue")

# -------

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


def draw_list_tasks(tasks: list):
    """Draws a div element with all the tasks div elements 
    """
    head = """<div id="task-list-2" class="task-list">"""

    task_list_html = """

      <div 
        style="display: flex;"
        class="task-element"
        id={task_id}>
            <div data-on:click="$selectedTask={task_id}; @post('/mark-completed');" class="check-btn"></div>
            {task_name} ->
            <span>{task_completed}</span>
             <div class="edit-delete-btns">
              <button class="btn">Edit</button>
              <button data-on:click=
                "$selectedTask={task_id}; @post('/delete-task');" 
              class="btn">Delete</button>
            </div>
      </div>
    """

    whole_element_html = head

    foot = """</div>"""

    for t in tasks:
        element_to_patch = task_list_html.format(
            task_id=t.id,
            task_name=t.name,
            task_completed=t.completed,
        )
        whole_element_html += element_to_patch

    whole_element_html += foot

    return whole_element_html


# ADD ONE TASK
# ------------


@app.post("/add-task")
@datastar_response
async def create_task(request: Request):
    signals = await read_signals(request)
    print(signals)
    title = signals["new_task"]
    new_task = data.create_task_obj(title)
    data.tasks.append(new_task)

    whole_element_html = draw_list_tasks(data.tasks)

    async def _():
        yield SSE.patch_elements(whole_element_html)
        yield SSE.patch_signals({"new_task": ""})

    return _()


delete_tasks_html = """<div id="task-list-2" class="task-list"></div>"""


# DELETE ALL TASKS
# ----------------


@app.post("/delete-all-tasks")
@datastar_response
async def delete_all_tasks(request: Request):
    data.tasks.clear()

    async def _():
        yield SSE.patch_elements(delete_tasks_html)

    return _()


# DELETE ONE TASK
# ---------------


@app.post("/delete-task")
@datastar_response
async def delete_task(request: Request):
    signals = await read_signals(request)
    ic(signals)
    whole_element_html = ...

    data.tasks = [
        task for task in data.tasks if task.id != int(signals["selectedTask"])
    ]

    whole_element_html = draw_list_tasks(data.tasks)

    async def _():
        yield SSE.patch_elements(whole_element_html)
        yield SSE.patch_signals({"new_task": ""})

    return _()


# MARK COMPLETED ONE TASK
# -----------------------


@app.post("/mark-completed")
@datastar_response
async def mark_completed(request: Request):
    signals = await read_signals(request)
    ic(signals)
    whole_element_html = """<div id="task-list-2" class="task-list">"""

    sel = int(signals["selectedTask"])
    for task in data.tasks:
        if task.id == sel:
            task.completed = not task.completed

    whole_element_html = draw_list_tasks(data.tasks)

    async def _():
        yield SSE.patch_elements(whole_element_html)
        yield SSE.patch_signals({"new_task": ""})

    return _()
