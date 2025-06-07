from fastapi import FastAPI
from pydantic import BaseModel
from app.rag.indexer import build_index
from app.rag.querier import ask_query

app = FastAPI()
index = build_index()

class QueryInput(BaseModel):
    question: str

@app.post("/query")
def query(input: QueryInput):
    answer = ask_query(index, input.question)
    return {"answer": answer}
