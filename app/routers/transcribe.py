import os
import requests
import whisper
import tempfile
from pydantic import BaseModel, Field
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.auth.dependencies import get_current_user

from app.tools.genai_client import generate_content
from app.tools.utils import clean_text


# Load the Whisper model
model = whisper.load_model("small")

router = APIRouter()


class TranscribeRequest(BaseModel):
    file_id: str = Field(..., example="1abc23XYZfileId")
    access_token: str = Field(..., example="ya29.a0ARrdaM-example-access-token")

GOOGLE_DRIVE_DOWNLOAD_URL = "https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"


def rephrase_text_structure_with_gemini(text: str):
    prompt = """
        Anda adalah seorang profesional dalam menyusun teks yang jelas, 
        terstruktur, dan mudah dipahami. Berikut adalah transkrip teks 
        hasil konversi dari audio (campuran dari Bahasa Indonesia dan Bahasa Inggris). 
        Tugas Anda adalah merapikan struktur 
        kalimat, memperbaiki tata bahasa, serta menyempurnakan gaya 
        penulisan agar lebih profesional dan alami tanpa mengubah makna aslinya. 
        Berikan hasil akhir dalam satu paragraf, tanpa baris baru, 
        tanpa simbol pemformatan, tanpa tanda kutip ("), 
        tanpa karakter garis miring terbalik (\\), dan tanpa karakter khusus lainnya. 
        Hasilkan hanya teks polos yang rapi dan mengalir alami. 
        Jangan sertakan penjelasan—langsung berikan hasil transkrip yang telah diperbaiki.
        Bila terdapat masalah atau error, cukup berikan respon "Error".
        Berikut transkrip yang perlu diperbaiki:
    """
    try:
        response = generate_content(
            contents=f"{prompt} {text}",
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/")
# async def transcribe_audio(file: UploadFile = File(...)):
#     # Create a temporary file with the original filename suffix
#     with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
#         input_path = tmp.name
#         tmp.write(await file.read())
    
#     # Perform transcription with stopwatch
#     try:
#         result = model.transcribe(input_path, fp16=False)
        
#         transcribe_result = result.get('text', 'N/A')
#         output = rephrase_text_structure_with_gemini(transcribe_result)
#     finally:
#         os.remove(input_path)  # Clean up the temporary file
        
#     return {'text': output}
    

@router.post(
    "/",
    summary="Transcribe audio from Google Drive",
    description="Fetches audio using Google Drive file ID and access token, then returns a cleaned transcription.",
    responses={
        200: {
            "description": "Successful transcription and cleaning",
            "content": {
                "application/json": {
                    "example": {
                        "text": "This lecture discusses reinforcement learning and its applications, such as Q-learning and MDPs."
                    }
                }
            }
        },
        400: {
            "description": "Bad Request - Failed to download audio",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to download audio from Google Drive"}
                }
            }
        },
        422: {
            "description": "Validation Error - Missing or invalid input format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "file_id"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error - Failed to process audio or AI output",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal Server Error"}
                }
            }
        }
    }
)
async def transcribe_audio(
    payload: TranscribeRequest,
):
    try:
        headers = {"Authorization": f"Bearer {payload.access_token}"}

        file_id = payload.file_id
        file_url = GOOGLE_DRIVE_DOWNLOAD_URL.format(file_id=file_id)

        # Download file from Google Drive
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            input_path = tmp.name
            response = requests.get(file_url, headers=headers, stream=True)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to download audio from Google Drive")
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)

        # Transcribe
        result = model.transcribe(input_path, fp16=False)
        transcribe_result = result.get("text", "N/A")
        output = rephrase_text_structure_with_gemini(transcribe_result)
        output = clean_text(output)

    except Exception as e:
        raise e
    finally:
        os.remove(input_path)
    
    return JSONResponse(content={"text": output})
