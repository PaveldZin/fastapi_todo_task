import uvicorn
from fastapi import FastAPI

from api import auth, tasks
from core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth.router)
app.include_router(tasks.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
