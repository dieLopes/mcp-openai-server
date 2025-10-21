from pydantic import BaseModel


class UserMessage(BaseModel):
    message: str

class MessageResponse(BaseModel):
    status: str
    message: str
    gpt_return: str | None = None
    command: dict | None = None
    result: dict | None = None