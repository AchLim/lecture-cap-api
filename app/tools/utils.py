import subprocess
import re

# sudo apt update && sudo apt install ffmpeg
def convert_to_wav(input_path: str, output_path: str):
    """
    Convert any audio file (MP3, M4A, OGG, etc.) to WAV using FFmpeg.
    """
    subprocess.run(
        ["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", output_path, "-y"], check=True
    )

def clean_text(text):
    """
    Cleans up transcribed text:
    - Removes backslashes
    - Removes escaped and regular double quotes
    - Converts '\\n' to real newlines
    """
    text = re.sub(r'\\"|\\|\"', '', text)
    return text
