import json
from fastapi.responses import JSONResponse
import requests
from fastapi import APIRouter
from app.configs.configs import Configs
from app.models.model import MessageResponse, UserMessage
from openai import OpenAI

from app.services.message_services import MessageService

router = APIRouter()


@router.post("/message", response_class=MessageResponse)
def receive_message(msg: UserMessage) -> MessageResponse:
    return MessageService.execute(msg)