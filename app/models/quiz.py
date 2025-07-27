from pydantic import BaseModel
from typing import List

class Answer(BaseModel):
    text: str
    is_correct: bool

class Question(BaseModel):
    question: str
    answers: List[Answer]

class QuizResponse(BaseModel):
    questions: List[Question]
    processing_time: float
    audio_duration: float
    message: str = "Quiz generated successfully"