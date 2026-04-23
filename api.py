import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from knowledge_base import KnowledgeBase
from content_pipeline import ContentPipeline

app = FastAPI(title="K.I.N.D. AI Fashion Content Creator", version="1.0.0")

# Serve the frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class GenerateRequest(BaseModel):
    client: str = "arket"
    content_format: str = "shoot_direction"
    category: str = "outerwear"
    mood: str = "minimal"


class IterateRequest(BaseModel):
    client: str = "arket"
    previous_content: str
    feedback: str


@app.get("/")
def root():
    index = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"message": "K.I.N.D. AI Fashion Content Creator API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "K.I.N.D. Content Creator"}


@app.get("/knowledge-base/{client}")
def get_knowledge_base(client: str):
    """Return the status of loaded knowledge base documents for a client."""
    try:
        kb = KnowledgeBase(client=client)
        kb.load()
        return kb.status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
def generate(req: GenerateRequest):
    """Generate brand-aligned fashion content."""
    valid_clients = ["arket", "cos", "mango"]
    if req.client not in valid_clients:
        raise HTTPException(status_code=400, detail=f"Client must be one of: {valid_clients}")

    try:
        kb = KnowledgeBase(client=req.client)
        kb.load()
        pipeline = ContentPipeline(knowledge_base=kb)
        result = pipeline.run(
            content_format=req.content_format,
            category=req.category,
            mood=req.mood,
        )
        return result
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
def compare(req: GenerateRequest):
    """Generate comparison: K.I.N.D. output vs generic ChatGPT output."""
    try:
        kb = KnowledgeBase(client=req.client)
        kb.load()
        pipeline = ContentPipeline(knowledge_base=kb)
        pipeline.run(
            content_format=req.content_format,
            category=req.category,
            mood=req.mood,
        )
        return pipeline.generate_comparison(req.content_format, req.category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/iterate")
def iterate(req: IterateRequest):
    """Refine previously generated content based on feedback."""
    try:
        kb = KnowledgeBase(client=req.client)
        kb.load()
        pipeline = ContentPipeline(knowledge_base=kb)
        refined = pipeline.iterate(req.previous_content, req.feedback)
        return {"content": refined, "client": req.client, "status": "iterated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
