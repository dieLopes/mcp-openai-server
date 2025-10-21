from fastapi import FastAPI
from app.routes import message
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    servers=[
        {'url': 'http://localhost:8000', 'description': 'Local Server'}
    ]
)

app.include_router(message.router)