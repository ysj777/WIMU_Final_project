from fastapi import FastAPI, Depends, Request, Response, status, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
#from .chatbot.website_tour_guide import Chatbot
from .chatbot.test_rag import Chatbot
import os
import configparser
import numpy as np
import pandas as pd
import google.generativeai as genai
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from starlette.middleware.sessions import SessionMiddleware
import textwrap
from pydantic import BaseModel

current_path = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(current_path, './config.ini'))

MAX_AGE = int(config['session']['max_age'])

class Chat(BaseModel):
    content: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://140.115.54.55:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=config['session']['key'],
    max_age=MAX_AGE,
)

@app.post("/api/create")
async def create_chatroom(response: Response):
    agent = Chatbot()
    response = agent.Greeting()
    return {'response': response}

@app.post("/api/chat")
async def chat(request: Request, response: Response,chat:Chat):
    agent = Chatbot()
    response = agent.Chat(user_input=chat.content)
    return {'response': response}