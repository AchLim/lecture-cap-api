import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from google import genai

from app.tools.genai_client import generate_content
from app.tools.utils import clean_text
from app.auth.dependencies import get_current_user

router = APIRouter()

# Request Model
class TextRequest(BaseModel):
    text: str = Field(..., example="Today we covered reinforcement learning and Markov decision processes...")

@router.post(
    "/",
    summary="Summarize lecture text using AI",
    description="Accepts lecture text and returns a concise summary using AI. Requires Bearer token authentication.",
    responses={
        200: {
            "description": "Successful summary generation",
            "content": {
                "application/json": {
                    "example": {
                        "summary": "The lecture covered reinforcement learning concepts such as MDPs and Q-learning."
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Token verification failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Token verification failed"}
                }
            }
        },
        422: {
            "description": "Validation Error - Invalid or missing text field",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "text"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error - AI summarization failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Something went wrong while generating the summary"}
                }
            }
        }
    }
)
async def summarize_text(request: TextRequest, user_data: any = Depends(get_current_user)):
    try:
        response = generate_content(
            contents=f"Summarize this lecture with output following the text language: {request.text}",
        )
        output = clean_text(response.text)
        return {"summary": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
