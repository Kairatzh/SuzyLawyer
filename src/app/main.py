import uvicorn

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

from src.rag_main.rag_inference import get_rag_answer, RAGConfig



app = FastAPI(
    title="SuzyLawyer assistant",
    version="1.0.0"
)



config = RAGConfig()

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str



@app.post("/get_question", response_model=AnswerResponse, summary="Задать юридический вопрос", tags=["RAG QA"])
async def get_question(request: QuestionRequest) -> Dict[str, str]:
    answer = get_rag_answer(request.question, config)
    return {"answer": answer}

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
