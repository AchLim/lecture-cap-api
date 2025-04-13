import uvicorn

from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.models import SecuritySchemeType

from fastapi.security import HTTPBearer
from app.routers import transcribe, summarize
from app.auth.dependencies import get_current_user

app = FastAPI(
    title="Lecture Cap API",
    summary="Lecture Cap is a mobile application designed to assist students in recording lectures, generating transcripts, and summarizing content using AI technology.",
    description="- Vincent Lim - 2231045\n- Jackson - 2231042\n- Jhony Susanto - 2231044\n- Erwin - 2231058\n- Josua Yoprisyanto - 2231082\n- Syasya Tri Puspita Dewi - 2231123\n",
    version="1.0.0",
    servers=[{
        'url': 'http://lcapapiv1noip.ddns.net',
    }]
)

# Secure routers
app.include_router(
    transcribe.router,
    prefix="/transcribe",
    tags=["Transcription"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    summarize.router,
    prefix="/summarize",
    tags=["Summarization"],
    dependencies=[Depends(get_current_user)]
)

@app.get("/")
def root():
    return {"message": "Welcome to Lecture Cap API"}

# ✅ Inject Bearer token into Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": 'http',
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == '__main__':
    uvicorn.run("main:app", port=8080, host='0.0.0.0', reload=True, reload_dirs=["html_files"])
