import json
from pathlib import Path
from fastapi.responses import JSONResponse
import requests
from fastapi import APIRouter
from app.configs.configs import Configs
from app.models.model import MessageResponse, UserMessage
from openai import OpenAI

from app.prompts import sheet_agent_prompt


client = OpenAI(api_key=Configs.OPENAI_API_KEY)

router = APIRouter()


@router.post("/message", response_class=JSONResponse)
def receive_message(msg: UserMessage):

    messages = sheet_agent_prompt.copy()
    messages.append({
        "role": "user",
        "content": f"Mensagem: {msg.message}"
    })

    completion = client.chat.completions.create(
        model=Configs.GPT_MODEL,
        messages=messages,
        temperature=0
    )

    command = completion.choices[0].message.content.strip()

    try:
        command_json = json.loads(command)
    except Exception as e:
        return MessageResponse(
            status="erro", 
            message=f"Não foi possível interpretar comando: {e}", 
            gpt_return=command
        )

    try:
        resp = requests.post(
            Configs.SHEET_MANIPULATOR_URL, 
            json=command_json,
            headers={"Content-Type": "application/json"}
        )
        return MessageResponse(
            status="sucesso", 
            message="Comando executado com sucesso.", 
            gpt_return=command,
            command=command_json,
            result=resp.json()
        )
    except Exception as e:
        return MessageResponse(
            status="erro", 
            message=f"Falha ao chamar serviço: {e}", 
            gpt_return=command,
            command=command_json
        )

@router.get("/mcp.json")
def manifest():
    path = Path(__file__).parent.parent / "mcp.json"
    with open(path) as f:
        data = json.load(f)
    return JSONResponse(content=data)