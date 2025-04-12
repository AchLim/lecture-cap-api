import os

from fastapi import APIRouter
from pydantic import BaseModel
# from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import BertTokenizer, EncoderDecoderModel

router = APIRouter()

# Get the absolute path of the current script
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))  
MODEL_DIR = os.path.join(PROJECT_DIR, "models")  # Store models inside "models/" at project root

# Define paths for transcription and summarization models
os.makedirs(MODEL_DIR, exist_ok=True)
# SUMMARIZE_MODEL_PATH = os.path.join(MODEL_DIR, "t5-summarizer")
SUMMARIZE_MODEL_PATH = os.path.join(MODEL_DIR, "bert-summarizer")
# MODEL_NAME = "cahya/t5-base-indonesian-summarization-cased"
MODEL_NAME = "cahya/bert2gpt-indonesian-summarization"

tokenizer = False
model = False

def ensure_model_exist():
    global tokenizer, model

    if not os.path.exists(SUMMARIZE_MODEL_PATH):
        # print("🔄 Downloading T5Tokenizer model...")
        # tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
        # model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
        print("🔄 Downloading BertTokenizer model...")
        tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
        model = EncoderDecoderModel.from_pretrained(MODEL_NAME)

        tokenizer.save_pretrained(SUMMARIZE_MODEL_PATH)
        model.save_pretrained(SUMMARIZE_MODEL_PATH)
        print("✅ Wav2Vec2 model downloaded and saved!")

ensure_model_exist()

# if not tokenizer:
#     tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)

# if not model:
#     model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

if not tokenizer:
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

if not model:
    model = EncoderDecoderModel.from_pretrained(MODEL_NAME)

tokenizer.bos_token = tokenizer.cls_token
tokenizer.eos_token = tokenizer.sep_token

# Request Model
class TextRequest(BaseModel):
    text: str

@router.post("/")
async def summarize_text(request: TextRequest):
    input_ids = tokenizer.encode(request.text, return_tensors='pt')

    min_length = 50
    max_length = 200
    
    summary_ids = model.generate(
        input_ids,
        min_length=min_length,
        max_length=max_length,
        num_beams=5,
        repetition_penalty=2.5,
        length_penalty=1.5,
        early_stopping=True,
        no_repeat_ngram_size=2,
        use_cache=True,
        do_sample=True,
        temperature=0.8,
        top_k=50,
        top_p=0.95
    )

    summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return {"summary": summary_text}
