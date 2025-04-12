import torch
import torchaudio
import subprocess
import os

from fastapi import APIRouter, File, UploadFile, HTTPException
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from app.tools.utils import convert_to_wav

router = APIRouter()

# Get the absolute path of the current script
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))  
MODEL_DIR = os.path.join(PROJECT_DIR, "models")  # Store models inside "models/" at project root

# Define paths for transcription and summarization models
TRANSCRIBE_MODEL_PATH = os.path.join(MODEL_DIR, "wav2vec2")
MODEL_NAME = "indonesian-nlp/wav2vec2-large-xlsr-indonesian"

# Ensure models directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

processor = False
model = False

def ensure_model_exist():
    global processor, model

    if not os.path.exists(TRANSCRIBE_MODEL_PATH):
        print("🔄 Downloading Wav2Vec2 model...")
        processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
        model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)

        processor.save_pretrained(TRANSCRIBE_MODEL_PATH)
        model.save_pretrained(TRANSCRIBE_MODEL_PATH)
        print("✅ Wav2Vec2 model downloaded and saved!")

ensure_model_exist()

if not processor:
    processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)

if not model:
    model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)

@router.post("/")
async def transcribe_audio(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    
    # Save uploaded file to a temporary file
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())
    
    output_wav = f"{input_path}.wav"

    try:
        convert_to_wav(input_path, output_wav)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail='FFmpeg conversion failed!')

    # Load the WAV file
    try:
        waveform, sample_rate = torchaudio.load(output_wav)
    except RuntimeError as e:
        print("Runtime Error: ", e)
        raise HTTPException(status_code=400, detail="Invalid audio file!")

    # Resample to 16kHz if needed
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)

    # Convert waveform to numpy for the processor
    speech_array = waveform.squeeze().numpy()

    inputs = processor(speech_array, sampling_rate=16_000, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    # Decode predictions to text
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]

    return {"text": transcription}
