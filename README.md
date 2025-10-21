# MCP OpenAI Server

Servidor MCP que utiliza o OpenAI para interpretar **mensagens em linguagem natural** e gerar comandos JSON para manipular planilhas do Google Sheets.

Ele funciona em conjunto com um **serviço executor** (`sheet-manipulator`) que realiza as operações na planilha.

---

## ⚙️ Funcionalidades

- Receber mensagens em linguagem natural do usuário.
- Converter a mensagem em um **comando JSON estruturado**.
- Enviar o comando para o serviço `sheet-manipulator`.
- Retornar o resultado da execução para o usuário.
- Expor um **manifesto MCP** (`/mcp.json`) para registro em agentes MCP.

---

## ⚡ Configuração

1. Crie um arquivo `.env` na raiz:

```
SHEET_MANIPULATOR_URL=http://localhost:5000/executar
OPENAI_API_KEY=your_openai_api_key_here
SHEET_NAME=Nome_planilha
GPT_MODEL=gpt-3.5-turbo
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Executando localmente
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

| Método | Endpoint  | Descrição                                                      |
|--------|-----------|----------------------------------------------------------------|
| POST   | /message  | Recebe mensagem do usuário, gera comando JSON e chama executor |
| GET    | /mcp.json | Retorna o manifesto MCP do servidor                            |

### Exemplo de requisição /message:
```json
{
  "mensagem": "Adicione uma despesa de 120 reais na categoria alimentação"
}
```

## 🧩 Arquitetura do fluxo

Usuário envia mensagem ao mcp-openai-server.

O servidor envia o prompt + mensagem para o OpenAI.

OpenAI retorna JSON estruturado.

Servidor chama o sheet-manipulator com o comando.

sheet-manipulator realiza operação na planilha Google Sheets.

Resultado é retornado ao usuário.

## 📝 Prompt configurável

O prompt do GPT está em:

app/prompts/sheet_agent_prompt.py

### Exemplo de estrutura:

```py
sheet_agent_prompt = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
]
```

### 📄 Manifesto MCP

O manifesto mcp.json descreve o servidor, suas ferramentas e schemas.
Exemplo de uso:

```bash
curl http://localhost:8000/mcp.json
```