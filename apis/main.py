from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from schemas.question_request_model import QuestionRequestModel, QuestionResponseModel
from schemas.upload_response import UploadResponse
import uuid
import os

from app.pdf_utils import load_document, splitting_docs
from app.rag import answer_question, build_vectorstore

app = FastAPI(title="Document Q&A")

SESSION_STORE = {}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR,exist_ok=True)

MODEL_VER = "1.0.0"

@app.get("/")
def message():
    return {"message":"Document Question and Answering chat bot."}

@app.get("/health")
def health_check():
    return{
        "status" : 200,
        "version" : MODEL_VER,
        "document_loaded" : bool(SESSION_STORE)
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only pdf files are supported.")

    file_path = os.path.join(UPLOAD_DIR,file.filename)
    with open(file_path,"wb") as f:
        content = await file.read()
        f.write(content)

    try:
        docs = load_document(file_path)
        if not docs:
            raise HTTPException(status_code=400, detail="Could not extract the docs.")

        chunks = splitting_docs(docs)
        vectorstore = build_vectorstore(chunks)

        session_id = str(uuid.uuid4())

        SESSION_STORE[session_id] = vectorstore

        return {
            "session_id":session_id
        }
    except Exception as e:
        return JSONResponse(status_code=500, content=str(e))

@app.post("/ask", response_model=QuestionResponseModel)
async def ask_question(payload: QuestionRequestModel):
    vectorstore = SESSION_STORE.get(payload.session_id) 

    if not vectorstore:
        raise HTTPException(status_code = 400, detail="Store not found. upload pdf first.")

    try:
        answer = answer_question(vectorstore,payload.question)
        return { "answer":answer }
    except Exception as e:
        return JSONResponse(status_code=500, content=str(e))