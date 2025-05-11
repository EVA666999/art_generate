import os
import sys

from fastapi import FastAPI

import uvicorn
from auth import auth, register

app = FastAPI()

app.include_router(auth.router)
app.include_router(register.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
