from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from models import Task

app = FastAPI()

SECRET_KEY = "super-secure-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Simulated database
users_db = {
    "admin": {
        "password": "secret",
        "tasks": {
            1: {"title": "Buy groceries", "description": "Milk, eggs, bread"},
        },
    }
}


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in users_db:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    return username


current_user_dependency = Annotated[str, Depends(get_current_user)]


@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


tasks_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@tasks_router.get("", summary="Get all tasks")
def read_tasks(username: current_user_dependency) -> dict[int, Task]:
    return users_db[username]["tasks"]


@tasks_router.get("/{task_id}", summary="Get a task by ID")
def read_task(task_id: int, username: current_user_dependency) -> Task:
    tasks = users_db[username]["tasks"]
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return tasks[task_id]


@tasks_router.post("", summary="Create a new task")
def create_task(task: Task, username: current_user_dependency):
    tasks = users_db[username]["tasks"]
    new_id = max(tasks.keys()) + 1 if tasks else 1
    tasks[new_id] = {
        "title": task.title,
        "description": task.description,
    }
    return {"success": True, "task_id": new_id}


@tasks_router.delete("/{task_id}", summary="Delete a task by ID")
def delete_task(task_id: int, username: current_user_dependency):
    tasks = users_db[username]["tasks"]
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    del tasks[task_id]
    return {"success": True}


app.include_router(tasks_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
