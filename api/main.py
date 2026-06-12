"""FastAPI后端 - 知识图谱问答系统"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from core.graph_store import GraphStore
from core.kg_builder import KGBuilder
from core.qa_engine import QAEngine

app = FastAPI(title="知识图谱问答系统", description="基于LLM的知识图谱构建与智能问答")
store = GraphStore()
builder = KGBuilder(store)
engine = QAEngine(store)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


class IngestRequest(BaseModel):
    text: str
    chunk_size: Optional[int] = 500

class AskRequest(BaseModel):
    question: str

class TripleRequest(BaseModel):
    subject: str
    relation: str
    object: str


@app.get("/")
async def index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.post("/ingest")
async def ingest(req: IngestRequest):
    result = builder.ingest_text(req.text, req.chunk_size)
    return {"status": "success", "data": result}

@app.post("/ask")
async def ask(req: AskRequest):
    result = engine.ask(req.question)
    return {"status": "success", "data": result}

@app.get("/graph")
async def get_graph():
    return {"status": "success", "data": store.get_graph_data()}

@app.get("/stats")
async def stats():
    return {"status": "success", "data": store.stats()}

@app.get("/triples")
async def triples():
    return {"status": "success", "data": store.get_all_triples()}

@app.post("/triple")
async def add_triple(req: TripleRequest):
    builder.add_manual_triple(req.subject, req.relation, req.object)
    return {"status": "success", "message": f"已添加: ({req.subject}, {req.relation}, {req.object})"}

@app.post("/search")
async def search_entity(keyword: str):
    results = store.search_entities(keyword)
    return {"status": "success", "data": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
