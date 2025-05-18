import os
import requests
import whisper
import tempfile
import json

from uuid import UUID
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
    note_id: UUID

GOOGLE_DRIVE_DOWNLOAD_URL = "https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
GOOGLE_DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media"
GOOGLE_DRIVE_CREATE_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=media"
GOOGLE_DRIVE_FILE_LIST_URL = (
    "https://www.googleapis.com/drive/v3/files"
    "?q=name='notes.json' and trashed=false"
    "&spaces=appDataFolder"
)



def rephrase_text_structure_with_gemini(text: str):
    prompt = """
        Anda adalah seorang profesional dalam menyusun teks yang jelas, terstruktur, dan mudah dipahami. Berikut adalah transkrip hasil konversi dari audio yang mungkin mengandung campuran Bahasa Indonesia dan Inggris.

        Tugas Anda:
        - Merapikan struktur kalimat
        - Memperbaiki tata bahasa
        - Menyempurnakan gaya penulisan agar terdengar profesional dan alami
        - Menentukan satu judul yang paling representatif terhadap isi transkrip

        Output HARUS mengikuti format persis berikut (tanpa baris baru, tanpa tanda kutip, tanpa simbol pemformatan seperti tanda bintang, garis miring, tanda petik, atau karakter khusus lainnya):

        JUDUL:::ISI_TRANSKRIPSI

        Keterangan:
        - Judul harus singkat, padat, dan relevan dengan isi transkrip.
        - ISI_TRANSKRIPSI harus berupa satu paragraf panjang, tidak dipisah baris, mengalir alami, dan mudah dipahami.

        Jika transkrip kosong, tidak terbaca, atau tidak dapat diproses, cukup hasilkan teks berikut (tanpa tambahan apa pun):

        Tidak dapat membuat ringkasan:::Transkripsi tidak tersedia atau tidak dapat diproses.

        Berikut transkrip yang perlu diperbaiki dan dirangkum:
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
        401: {
            "description": "Unauthorized - Token verification failed",
            "content": {
                "application/json": {
                    "example": {"detail": "Token verification failed"}
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

        file_url = GOOGLE_DRIVE_DOWNLOAD_URL.format(file_id=payload.file_id)

        # 1. Download audio from user's Google Drive
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            input_path = tmp.name
            response = requests.get(file_url, headers=headers, stream=True)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to download audio from Google Drive")
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)

        # 2. Transcribe using Whisper
        result = model.transcribe(input_path, fp16=False)
        raw_text = result.get("text", "").strip()

        # 3. Clean using Gemini + utility
        cleaned_text = clean_text(rephrase_text_structure_with_gemini(raw_text))
        if ':::' in cleaned_text:
            title, content = cleaned_text.split(':::', 1)
        else:
            title = "Tidak dapat membuat ringkasan"
            content = "Transkripsi tidak tersedia atau tidak dapat diproses."

        # Step 4: Read current notes.json (if exists)
        notes = []
        notes_file_id = None
        list_resp = requests.get(GOOGLE_DRIVE_FILE_LIST_URL, headers=headers)
        if list_resp.ok:
            files = list_resp.json().get("files", [])
            if files:
                notes_file_id = files[0]["id"]
                notes_resp = requests.get(GOOGLE_DRIVE_DOWNLOAD_URL.format(file_id=notes_file_id), headers=headers)
                if notes_resp.ok:
                    try:
                        notes = notes_resp.json()
                    except Exception:
                        notes = []
        
        # Step 5: Update existing note instead of appending
        updated_note = None
        for note in notes:
            if note.get("id") == str(payload.note_id):
                note.update({
                    'title': title,
                    'isTranscribed': True,
                    'content': content,
                    'originalContent': content,
                })
                updated_note = note
                break

        if not updated_note:
            raise HTTPException(status_code=404, detail="Note not found in notes.json")


        # Step 7: Save updated notes.json
        update_resp = requests.patch(
            GOOGLE_DRIVE_UPLOAD_URL.format(file_id=notes_file_id),
            headers={
                **headers,
                "Content-Type": "application/json"
            },
            data=json.dumps(notes),
        )
        if not update_resp.ok:
            raise HTTPException(status_code=500, detail="Failed to update notes.json on Google Drive")

        return JSONResponse(content={"success": True, "message": "Note transcribed successfully."})

    except Exception as e:
        raise e
    finally:
        os.remove(input_path)
    
    return JSONResponse(content={"message": "Note updated successfully.", "note_id": str(payload.note_id)})