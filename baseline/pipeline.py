from fastapi import FastAPI
from pydantic import BaseModel
from baseline.retriever.retriever import build_index
from baseline.generator.generator import ask_query

app = FastAPI()
index = build_index()

class QueryInput(BaseModel):
    question: str

@app.post("/query")
def query(input: QueryInput):
    answer = ask_query(index, input.question)
    return {"answer": answer}
