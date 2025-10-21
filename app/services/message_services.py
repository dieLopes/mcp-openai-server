import json
from openai import OpenAI
import requests
from app.configs.configs import Configs
from app.models.model import UserMessage, MessageResponse
from app.prompts.sheet_agent_prompt import sheet_agent_prompt

openai_client = OpenAI(api_key=Configs.OPENAI_API_KEY)


class MessageService:

    @staticmethod
    def execute(msg: UserMessage) -> MessageResponse:
        """
        Envia a mensagem do usuário para o GPT, interpreta o comando retornado
        e executa no servidor MCP via /execute.
        """

        # 1️⃣ Monta o contexto do agente
        messages = sheet_agent_prompt[:]
        messages.append({
            "role": "user",
            "content": f"Mensagem: {msg.message}"
        })

        # 2️⃣ Gera o comando via GPT
        completion = openai_client.chat.completions.create(
            model=Configs.GPT_MODEL,
            messages=messages,
            temperature=0
        )

        command = completion.choices[0].message.content.strip()

        # 3️⃣ Tenta interpretar o comando como JSON
        try:
            command_json = json.loads(command)
        except Exception as e:
            return MessageResponse(
                status="erro",
                message=f"Não foi possível interpretar o comando retornado pelo GPT: {e}",
                gpt_return=command
            )

        # 4️⃣ Valida a tool no manifesto do MCP
        try:
            manifest_url = f"{Configs.SHEET_MCP_URL}/mcp.json"
            manifest = requests.get(manifest_url, timeout=5).json()
            available_tools = [t["name"] for t in manifest.get("tools", [])]

            tool_name = command_json.get("tool")

            if tool_name not in available_tools:
                return MessageResponse(
                    status="erro",
                    message=f"A ferramenta '{tool_name}' não existe no servidor MCP.",
                    gpt_return=command,
                    command=command_json
                )
        except Exception as e:
            return MessageResponse(
                status="erro",
                message=f"Falha ao consultar manifesto MCP: {e}",
                gpt_return=command,
                command=command_json
            )

        # 5️⃣ Executa a tool no servidor MCP
        try:
            execute_url = f"{Configs.SHEET_MCP_URL}/execute"
            payload = {
                "tool": tool_name,
                "args": command_json.get("args", {})
            }

            resp = requests.post(
                execute_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            return MessageResponse(
                status="sucesso" if resp.ok else "erro",
                message="Comando executado com sucesso." if resp.ok else f"Falha ao executar: {resp.text}",
                gpt_return=command,
                command=command_json,
                result=resp.json() if resp.ok else None
            )

        except Exception as e:
            return MessageResponse(
                status="erro",
                message=f"Erro ao chamar o servidor MCP: {e}",
                gpt_return=command,
                command=command_json
            )
