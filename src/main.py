from fastapi import FastAPI, HTTPException
from models import Task
import uvicorn

app = FastAPI()

tasks = {
    1: {"title": "Buy groceries", "description": "Milk, eggs, bread"},
}


@app.get("/tasks", tags=["tasks"], summary="Get all tasks")
def read_tasks() -> dict[int, Task]:
    return tasks


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get a task by ID")
def read_task(task_id: int) -> Task:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.post("/tasks", tags=["tasks"], summary="Create a new task")
def create_task(task: Task):
    new_id = max(tasks.keys()) + 1
    tasks[new_id] = {
        "title": task.title,
        "description": task.description,
    }
    return {"success": True, "task_id": new_id}

@app.delete("/tasks/{task_id}", tags=["tasks"], summary="Delete a task by ID")
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
    return {"success": True}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
