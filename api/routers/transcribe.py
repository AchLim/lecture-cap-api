import os
import whisper
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException

from api.tools.genai_client import generate_content


# Load the Whisper model
model = whisper.load_model("small")

router = APIRouter()

def rephrase_text_structure_with_gemini(text: str):
    prompt = """
        Anda adalah seorang profesional dalam menyusun teks yang jelas, 
        terstruktur, dan mudah dipahami. Berikut adalah transkrip teks 
        hasil konversi dari audio. Tugas Anda adalah merapikan struktur 
        kalimat, memperbaiki tata bahasa, serta menyempurnakan gaya 
        penulisan agar lebih profesional dan alami tanpa mengubah makna aslinya. 
        Berikan hasil akhir dalam satu paragraf, tanpa baris baru, 
        tanpa simbol pemformatan, tanpa tanda kutip ("), 
        tanpa karakter garis miring terbalik (\\), dan tanpa karakter khusus lainnya. 
        Hasilkan hanya teks polos yang rapi dan mengalir alami. 
        Jangan sertakan penjelasan—langsung berikan hasil transkrip yang telah diperbaiki.
        Berikut transkrip yang perlu diperbaiki:
    """
    try:
        response = generate_content(
            contents=f"{prompt} {text}",
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Create a temporary file with the original filename suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
        input_path = tmp.name
        tmp.write(await file.read())
    
    # Perform transcription with stopwatch
    try:
        result = model.transcribe(input_path, fp16=False)
        
        transcribe_result = result.get('text', 'N/A')
        output = rephrase_text_structure_with_gemini(transcribe_result)
    finally:
        os.remove(input_path)  # Clean up the temporary file
        
        return {'text': output}
    
