from dotenv import load_dotenv
import os

load_dotenv()

class Configs:
    
    OPENAI_API_KEY: str = "your_openai_api_key_here"
    GPT_MODEL: str = os.getenv("GPT_MODEL", "gpt-3.5-turbo")
    
    SHEET_MCP_URL: str = os.getenv("SHEET_MCP_URL", "http://localhost:5000/executar")
    SHEET_NAME: str = os.getenv("SHEET_NAME")
    