import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from google import genai

from app.tools.genai_client import generate_content
from app.auth.dependencies import get_current_user

router = APIRouter()

# Request Model
class TextRequest(BaseModel):
    text: str

@router.post("/")
async def summarize_text(request: TextRequest, user_data: any = Depends(get_current_user)):
    try:
        response = generate_content(
            contents=f"Summarize this lecture with output following the text language: {request.text}",
        )
        return {"summary": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
