# 🎤 Lecture Cap API  

## 📌 Project Overview  
Lecture Cap API is a speech-to-text transcription and summarization API designed to process lecture recordings. Users can upload audio files, transcribe spoken content into text using Whisper, and generate clean, structured summaries using Google's Gemini (via `genai`). Ideal for students, educators, and e-learning platforms.

## 🚀 Features  
- 🎧 **Speech-to-Text** – Convert lecture audio into accurate text transcripts using OpenAI Whisper.  
- ✍️ **Text Summarization** – Generate concise and language-consistent summaries with Google Gemini.  
- 🧹 **Text Cleanup** – Automatically rephrase and polish transcripts for clarity and professionalism.  
- 📂 **Audio File Upload** – Supports formats like MP3, WAV, M4A, etc.  
- 🌍 **Multi-Language Ready** – Whisper supports multiple languages natively.  

## 🛠️ Installation  
1. Clone the repository:  
   ```sh  
   git clone https://github.com/AchLim/lecture-cap-api.git  
   cd lecture-cap-api  
   ```  
2. Install dependencies:  
   ```sh  
   pip install -r requirements.txt 
   ```  
3. Create a `.env` file to store your API keys:
   ```env
   GOOGLE_API_KEY=your_google_genai_api_key
   ```

## 📡 API Endpoints  

| Method | Endpoint | Description |  
|--------|----------|-------------|  
| `POST` | `/transcribe` | Upload an audio file to transcribe and clean up the output |  
| `POST` | `/summarize` | Generate a summary from raw or cleaned transcription text |  

## 🏗️ Technologies Used  
- **Backend**: FastAPI  
- **Speech Recognition**: OpenAI Whisper  
- **Summarization & Text Cleanup**: Google Gemini (via `genai`)  

## 🔧 Model Used  
Lecture Cap API uses the **Whisper model** for speech recognition:
```python
import whisper
model = whisper.load_model("small")
```
This model is capable of transcribing multilingual audio with high accuracy.

## 📜 License  
This project is licensed under the MIT License.  

## 🤝 Contributing  
We welcome contributions! Feel free to fork the repo, create a new branch, and submit a pull request.