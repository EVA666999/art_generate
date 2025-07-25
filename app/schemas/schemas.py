from pydantic import BaseModel
from typing import List, Dict, Any


class CreateUser(BaseModel):
    email: str
    username: str
    password: str


