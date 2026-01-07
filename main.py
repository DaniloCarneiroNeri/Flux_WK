import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import routes

app = FastAPI(title="Flux API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://prototype-solution-1.onrender.com" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

if os.path.exists("static"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_vue_app(full_path: str):
    possible_file = os.path.join("static", full_path)
    if os.path.exists(possible_file) and os.path.isfile(possible_file):
        return FileResponse(possible_file)
    
    return FileResponse("static/index.html")