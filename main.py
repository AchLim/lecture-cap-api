import torch
import torchaudio
import os
import subprocess

from fastapi import FastAPI, File, UploadFile, HTTPException
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

app = FastAPI()

# Load Wav2Vec2 model for Indonesian (from Hugging Face)
MODEL_NAME = "indonesian-nlp/wav2vec2-large-xlsr-indonesian"
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)

def convert_to_wav(input_path: str, output_path: str):
    """
    Convert any audio file (MP3, M4A, OGG, etc.) to WAV using FFmpeg.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", output_path, "-y"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail='FFmpeg conversion failed!')


@app.get("/")
async def main():
    return {'status': 200, 'message': 'Hello World'}

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    
    # Save uploaded file to a temporary file
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())
    
    output_wav = f"{input_path}.wav"

    convert_to_wav(input_path, output_wav)

    # Load the WAV file
    try:
        waveform, sample_rate = torchaudio.load(output_wav)
    except RuntimeError as e:
        print(e)
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
