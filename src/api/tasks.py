from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from models import Task
from core.database import users_db
from core.security import get_current_user

current_user_dependency = Annotated[str, Depends(get_current_user)]

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", summary="Get all tasks")
def read_tasks(username: current_user_dependency) -> dict[int, Task]:
    return users_db[username]["tasks"]


@router.get("/{task_id}", summary="Get a task by ID")
def read_task(task_id: int, username: current_user_dependency) -> Task:
    tasks = users_db[username]["tasks"]
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return tasks[task_id]


@router.post("", summary="Create a new task")
def create_task(task: Task, username: current_user_dependency):
    tasks = users_db[username]["tasks"]
    new_id = max(tasks.keys()) + 1 if tasks else 1
    tasks[new_id] = {
        "title": task.title,
        "description": task.description,
    }
    return {"success": True, "task_id": new_id}


@router.delete("/{task_id}", summary="Delete a task by ID")
def delete_task(task_id: int, username: current_user_dependency):
    tasks = users_db[username]["tasks"]
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    del tasks[task_id]
    return {"success": True}
