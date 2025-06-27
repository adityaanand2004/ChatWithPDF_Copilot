from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import uuid4
import os

from pdf_utils import extract_text_from_pdf
from vector_store import store_document, retrieve_context
from ai_chat import ask_with_context
from chat_db import SessionLocal, ChatHistory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_sessions = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)
    store_document(text)
    return {"message": "PDF processed"}

@app.post("/ask/")
async def ask(
    question: str = Form(...),
    session_id: str = Form(None),
    db: Session = Depends(get_db)
):
    if not session_id:
        session_id = str(uuid4())

    history = chat_sessions.get(session_id, [
        {"role": "system", "content": "You are a helpful assistant."}
    ])
    history.append({"role": "user", "content": question})

    context = retrieve_context(question)
    answer = ask_with_context(question, context)

    history.append({"role": "assistant", "content": answer})
    chat_sessions[session_id] = history

    chat_record = ChatHistory(session_id=session_id, user_message=question, ai_response=answer)
    db.add(chat_record)
    db.commit()

    return {"answer": answer, "session_id": session_id}

@app.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    items = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).all()
    return [{"q": i.user_message, "a": i.ai_response} for i in items]

@app.get("/")
def root():
    return {"message": "ChatGPT Clone Backend Running ✅"}

