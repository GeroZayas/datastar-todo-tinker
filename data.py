from dataclasses import dataclass
from uuid import uuid4

@dataclass
class Task:
	id: int
	name: str
	description: str
	completed: bool

example_task = Task(1, "Clean", "", False)
tasks = [example_task, ]

def create_task_obj(name, desc = "") -> Task:
	"""Returns a Task obj"""
	id = uuid4()
	if desc == "":
		desc = "No description"
	completed = False
	t = Task(id, name.capitalize(), desc.capitalize(), completed)
	return t