import openai
import json
import os
from typing import List
from app.models.quiz import Question, Answer


class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Set up OpenAI client (for newer versions)
        openai.api_key = api_key
        print("OpenAI API initialized successfully!")

    async def generate_questions(self, transcript: str) -> List[Question]:
        """
        Generate 5 multiple choice questions from transcript
        """
        if len(transcript.strip()) < 50:
            raise Exception("Transcript too short to generate meaningful questions")

        prompt = f"""
        Based on the following transcript from an educational session, create exactly 5 multiple choice questions.
        Each question should have 4 options with only one correct answer.

        Make sure questions:
        1. Test understanding of key concepts from the session
        2. Are clear and unambiguous
        3. Have realistic but incorrect distractors
        4. Cover different parts of the content

        Transcript: {transcript}

        Please respond with ONLY a valid JSON array in this exact format (no additional text):
        [
            {{
                "question": "What is the main concept discussed about...?",
                "answers": [
                    {{"text": "Option A", "is_correct": false}},
                    {{"text": "Option B", "is_correct": true}},
                    {{"text": "Option C", "is_correct": false}},
                    {{"text": "Option D", "is_correct": false}}
                ]
            }}
        ]
        """

        try:
            print("Generating questions with OpenAI...")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator who creates high-quality multiple choice questions. Respond only with valid JSON, no additional text."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            content = response.choices[0].message.content.strip()
            print(f"OpenAI response received: {len(content)} characters")

            # Parse JSON response
            questions_data = json.loads(content)

            if not isinstance(questions_data, list) or len(questions_data) != 5:
                raise Exception(
                    f"Expected 5 questions, got {len(questions_data) if isinstance(questions_data, list) else 'invalid format'}")

            # Convert to Pydantic models
            questions = []
            for i, q_data in enumerate(questions_data):
                try:
                    answers = [Answer(**answer) for answer in q_data["answers"]]

                    # Verify exactly one correct answer
                    correct_count = sum(1 for answer in answers if answer.is_correct)
                    if correct_count != 1:
                        raise Exception(f"Question {i + 1}: Must have exactly 1 correct answer, found {correct_count}")

                    question = Question(question=q_data["question"], answers=answers)
                    questions.append(question)

                except Exception as e:
                    raise Exception(f"Error processing question {i + 1}: {str(e)}")

            print(f"Successfully generated {len(questions)} questions")
            return questions

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response content: {content}")
            raise Exception("AI service returned invalid JSON format")
        except Exception as e:
            print(f"AI service error: {str(e)}")
            raise Exception(f"AI question generation failed: {str(e)}")