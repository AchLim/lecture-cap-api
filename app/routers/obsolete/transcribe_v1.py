import os
from fastapi import APIRouter, File, UploadFile, HTTPException

from haystack.components.audio import LocalWhisperTranscriber

router = APIRouter()

# Initialize the transcriber
transcriber = LocalWhisperTranscriber(model='turbo')
transcriber.warm_up()

@router.post("/")
async def transcribe_audio(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    
    # Save uploaded file to a temporary file
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())

    # Perform transcription
    try:
        print(input_path)
        transcription = transcriber.run(sources=[f'./{input_path}'])
        transcribed_text = transcription['documents'][0].content
        return {'text': transcribed_text}
    finally:
        os.remove(input_path)  # Clean up the temporary file
    
    result = transcriber.transcribe(input_path)
    print(result)
    return {'text': result}
    
    # output_wav = f"{input_path}.wav"

    # try:
    #     convert_to_wav(input_path, output_wav)
    # except subprocess.CalledProcessError:
    #     raise HTTPException(status_code=500, detail='FFmpeg conversion failed!')

    # # Load the WAV file
    # try:
    #     waveform, sample_rate = torchaudio.load(output_wav)
    # except RuntimeError as e:
    #     print("Runtime Error: ", e)
    #     raise HTTPException(status_code=400, detail="Invalid audio file!")

    # # Resample to 16kHz if needed
    # if sample_rate != 16000:
    #     resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
    #     waveform = resampler(waveform)

    # # Convert waveform to numpy for the processor
    # speech_array = waveform.squeeze().numpy()

    # inputs = processor(speech_array, sampling_rate=16_000, return_tensors="pt", padding=True)

    # with torch.no_grad():
    #     logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    # # Decode predictions to text
    # predicted_ids = torch.argmax(logits, dim=-1)
    # transcription = processor.batch_decode(predicted_ids)[0]

    # return {"text": transcription}
