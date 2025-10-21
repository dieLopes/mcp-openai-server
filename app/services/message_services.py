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
        Consulta o manifesto MCP, envia-o para o GPT como contexto,
        e então executa o comando gerado no servidor MCP.
        """
        try:
            # 1️⃣ Lê o manifesto MCP
            manifest_url = f"{Configs.SHEET_MANIPULATOR_URL}/mcp.json"
            manifest = requests.get(manifest_url, timeout=5).json()
        except Exception as e:
            return MessageResponse(
                status="erro",
                message=f"Falha ao consultar manifesto MCP: {e}"
            )

        # 2️⃣ Monta o prompt incluindo as tools do manifesto
        tools_description = "\n".join([
            f"- {tool['name']}: {tool.get('description', '')}"
            for tool in manifest.get("tools", [])
        ])

        system_prompt = (
            f"Você é um agente MCP. As ferramentas disponíveis são:\n{tools_description}\n\n"
            "Dado o pedido do usuário, gere um JSON no formato aceito pela ferramenta apropriada.\n"
            "Retorne **apenas o JSON**, sem explicações."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg.message}
        ]

        # 3️⃣ GPT gera o comando JSON
        completion = openai_client.chat.completions.create(
            model=Configs.GPT_MODEL,
            messages=messages,
            temperature=0
        )

        command = completion.choices[0].message.content.strip()

        # 4️⃣ Interpreta o comando como JSON
        try:
            command_json = json.loads(command)
        except Exception as e:
            return MessageResponse(
                status="erro",
                message=f"Não foi possível interpretar o comando: {e}",
                gpt_return=command
            )

        # 5️⃣ Executa no servidor MCP
        try:
            execute_url = f"{Configs.SHEET_MANIPULATOR_URL}/execute"
            resp = requests.post(
                execute_url,
                json=command_json,
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