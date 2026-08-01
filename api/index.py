from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import hashlib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks = {}

class GenReq(BaseModel):
    title: str
    duration: int = 180

@app.get("/api/")
def root():
    return {"service": "Drama AI", "status": "running"}

@app.post("/api/generate")
def generate(req: GenReq):
    tid = "t_" + hashlib.md5(f"{req.title}{time.time()}".encode()).hexdigest()[:8]
    tasks[tid] = {"task_id": tid, "title": req.title, "status": "processing", "progress": 0, "message": "Starting...", "started": time.time()}
    return {"task_id": tid, "status": "queued"}

@app.get("/api/status/{task_id}")
def status(task_id: str):
    if task_id not in tasks:
        return {"error": "Not found"}
    t = tasks[task_id]
    e = time.time() - t["started"]
    if e < 3: t.update({"progress": min(20, int(e*7)), "message": "Writing script..."})
    elif e < 6: t.update({"progress": min(50, 20+int((e-3)*10)), "message": "Generating scenes..."})
    elif e < 10: t.update({"progress": min(90, 50+int((e-6)*10)), "message": "Rendering..."})
    else: t.update({"progress": 100, "status": "completed", "message": "Done!", "video_url": "https://example.com/v.mp4"})
    return t

# WAJIB: Handler untuk Vercel serverless
from mangum import Mangum
handler = Mangum(app)
