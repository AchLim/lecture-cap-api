<<<<<<< HEAD
# lecture-cap-api
Lecture Cap API is a FastAPI-based application that transcribes speech to text and summarizes lecture recordings. It leverages Wav2Vec2 for Indonesian speech recognition and NLP models for summarization, making it ideal for students, educators, and e-learning platforms.
=======
# 🎤 Lecture Cap API  

## 📌 Project Overview  
Lecture Cap API is a speech-to-text transcription and summarization API designed to process lecture recordings. It enables users to upload audio files, transcribe spoken content into text, and generate concise summaries for quick review. Ideal for students, educators, and e-learning platforms.  

## 🚀 Features  
- 🎙️ **Speech-to-Text** – Convert lecture audio into accurate text transcripts.  
- ✍️ **Text Summarization** – Generate concise summaries of transcriptions.  
- 📂 **Audio File Upload** – Supports multiple audio formats (MP3, WAV, etc.).  
- 🌍 **Multi-Language Support** – Process lectures in different languages.  
- 🔍 **Keyword Extraction** – Identify key topics and important phrases.  

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

## 📡 API Endpoints  
| Method | Endpoint | Description |  
|--------|---------|-------------|  
| `POST` | `/transcribe` | Upload an audio file for transcription |  
| `POST` | `/summarize` | Generate a summary from a transcription |  

## 🏗️ Technologies Used  
- **Backend**: FastAPI
- **Speech Recognition**: Wav2Vec2  
- **Summarization**: GPT / BERT-based NLP models  

## 🔧 Model Used  
Lecture Cap API uses the **Wav2Vec2 model** for speech recognition, specifically:  
```python  
MODEL_NAME = "indonesian-nlp/wav2vec2-large-xlsr-indonesian"  
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)  
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)  
```  
This model is optimized for **Indonesian speech recognition**, allowing high-accuracy transcription of spoken content.  

## 📜 License  
This project is licensed under the MIT License.  

## 🤝 Contributing  
We welcome contributions! Feel free to fork the repo, create a new branch, and submit a pull request.  
>>>>>>> efaa2cb (Initial commit)
