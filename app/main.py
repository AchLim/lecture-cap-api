import uvicorn

from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.models import SecuritySchemeType

from fastapi.security import HTTPBearer
from app.routers import transcribe, summarize
from app.auth.dependencies import get_current_user

app = FastAPI(
    title="Lecture Cap API",
    summary="""
        Lecture Cap is a mobile application developed to support students in recording lectures, generating transcripts, and summarizing content using advanced AI technology.
    """,
    description="""The application utilizes Firebase Authentication to manage user authentication, ensuring secure access through tokens handled by Firebase. Additionally, it integrates with Google Drive for external data storage, enabling efficient and reliable management of notes and audio recordings.\n
- Vincent Lim - 2231045\n- Jackson - 2231042\n- Jhony Susanto - 2231044\n- Erwin - 2231058\n- Josua Yoprisyanto - 2231082\n- Syasya Tri Puspita Dewi - 2231123
    """,
    version="1.0.0",
    servers=[{
        'url': 'http://lcapapiv1noip.ddns.net',
        'description': 'Main Production Server'
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

@app.get(
    "/",
    tags=["Root"],
    summary="Root Endpoint",
    description="Returns a welcome message for the Lecture Cap API.",
    responses={
        200: {
            "description": "API is reachable",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to Lecture Cap API"
                    }
                }
            }
        }
    }
)
def root():
    return {"message": "Welcome to Lecture Cap API"}

@app.get(
    "/ping",
    tags=["Health Check"],
    summary="Health check endpoint",
    description="Simple endpoint to verify if the API is running.",
    responses={
        200: {
            "description": "API is healthy and reachable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok"
                    }
                }
            }
        }
    }
)
def ping():
    return {"status": "ok"}

# ✅ Inject Bearer token into Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        summary=app.summary,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=app.servers,
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
