import os
import sys

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
import uvicorn
from app.auth import auth, register
from app.routers import art_generate, test_gen
from app.api.test_ai_chat import app as story_generator_app

app = FastAPI()

app.include_router(auth.router)
app.include_router(register.router)
app.include_router(art_generate.router)
# app.include_router(test_gen.router)
app.include_router(story_generator_app.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)