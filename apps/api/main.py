# apps/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import candidates, generate_summary

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # use "*" for dev if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router)
app.include_router(generate_summary.router)