import whisper
import tempfile
import os
import aiofiles
from typing import Tuple


class AudioProcessor:
    def __init__(self):
        # Load Whisper model (base is good balance of speed vs accuracy)
        print("Loading Whisper model...")
        self.model = whisper.load_model("base")
        print("Whisper model loaded successfully!")

    async def transcribe_audio(self, audio_file_path: str) -> Tuple[str, float]:
        """
        Convert audio file to text using Whisper
        Returns: (transcript, duration_seconds)
        """
        try:
            print(f"Transcribing audio file: {audio_file_path}")
            result = self.model.transcribe(audio_file_path)

            transcript = result["text"].strip()
            duration = result.get("segments", [{}])[-1].get("end", 0) if result.get("segments") else 0

            print(f"Transcription completed. Duration: {duration}s")
            print(f"Transcript preview: {transcript[:100]}...")

            return transcript, duration

        except Exception as e:
            print(f"Transcription error: {str(e)}")
            raise Exception(f"Audio transcription failed: {str(e)}")

    async def save_uploaded_file(self, upload_file) -> str:
        """
        Save uploaded file temporarily
        """
        try:
            # Create temporary file with proper extension
            file_extension = os.path.splitext(upload_file.filename)[1] or ".wav"

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                # Read file content
                content = await upload_file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name

            print(f"File saved temporarily: {temp_file_path}")
            return temp_file_path

        except Exception as e:
            print(f"File saving error: {str(e)}")
            raise Exception(f"File saving failed: {str(e)}")

    def cleanup_file(self, file_path: str):
        """
        Remove temporary file
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            print(f"Cleanup warning: {str(e)}")