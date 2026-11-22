# server.py
from fastapi import FastAPI
from pydantic import BaseModel
import search_tool  # your existing module

app = FastAPI()

class SearchReq(BaseModel):
    query: str
    max_results: int = 5

class FetchReq(BaseModel):
    url: str

@app.post("/search")
async def search(req: SearchReq):
    result = await search_tool.run(req.query)
    return {"results": result["results"][: req.max_results], "timings": result["timings"]}

@app.post("/fetch")
async def fetch(req: FetchReq):
    import httpx
    async with httpx.AsyncClient(follow_redirects=True) as c:
        text = await search_tool.jina_fetch(c, req.url)
    return {"url": req.url, "text": text}

@app.get("/health")
def health():
    return {"ok": True}