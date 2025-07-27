from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.audio_processor import AudioProcessor
from app.services.ai_service import AIService
from app.models.quiz import QuizResponse
import time
import os

router = APIRouter()

# Initialize services (these will be loaded when the module is imported)
audio_processor = AudioProcessor()
ai_service = AIService()


@router.post("/upload-audio", response_model=QuizResponse)
async def upload_audio(file: UploadFile = File(...)):
    """
    Main endpoint: Upload audio file and get generated questions
    """
    start_time = time.time()
    temp_file_path = None

    try:
        print(f"Received file upload: {file.filename}, type: {file.content_type}")

        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail=f"File must be an audio file. Received: {file.content_type}"
            )

        # Check file size (limit to 50MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 50MB."
            )

        # Step 1: Save uploaded file temporarily
        temp_file_path = await audio_processor.save_uploaded_file(file)

        # Step 2: Convert audio to text
        transcript, duration = await audio_processor.transcribe_audio(temp_file_path)

        if not transcript.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful text from audio. Please check if the audio has clear speech."
            )

        if len(transcript.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Audio transcript too short to generate meaningful questions. Please upload a longer recording."
            )

        # Step 3: Generate questions using AI
        questions = await ai_service.generate_questions(transcript)

        if len(questions) == 0:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate questions from the audio content"
            )

        processing_time = time.time() - start_time
        print(f"Processing completed in {processing_time:.2f} seconds")

        return QuizResponse(
            questions=questions,
            processing_time=round(processing_time, 2),
            audio_duration=round(duration, 2),
            message=f"Successfully generated {len(questions)} questions from {duration:.1f}s audio"
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if temp_file_path:
            audio_processor.cleanup_file(temp_file_path)


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the router is working"""
    return {
        "message": "Upload router is working!",
        "endpoints": [
            "POST /api/upload-audio - Upload audio file and generate quiz"
        ]
    }