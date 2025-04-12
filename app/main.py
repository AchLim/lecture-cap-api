import uvicorn

from fastapi import FastAPI
from app.routers import transcribe, summarize

app = FastAPI(title="Lecture Cap API")

# Include API routes
app.include_router(transcribe.router, prefix="/transcribe", tags=["Transcription"])
app.include_router(summarize.router, prefix="/summarize", tags=["Summarization"])

@app.get("/")
def root():
    return {"message": "Welcome to Lecture Cap API"}

if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, host='0.0.0.0', reload = True, reload_dirs = ["html_files"])
