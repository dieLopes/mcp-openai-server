from typing import Optional
from pydantic import BaseModel


class UserMessage(BaseModel):
    message: str

class MessageResponse(BaseModel):
    status: str
    message: str
    gpt_return: Optional[dict] = None
    command: Optional[dict] = None
    result: Optional[dict] = None