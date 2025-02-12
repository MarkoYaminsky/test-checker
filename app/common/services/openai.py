import json
import logging

import openai

from app.core.config import settings
from app.student_tests.models import StudentTestAnswer

client = openai.Client(api_key=settings.openai_api_key)
logger = logging.getLogger(__name__)


def get_student_answer_grid(student_answer: StudentTestAnswer) -> dict[int, list[int]]:
    prompt = (
        "I am a teacher grading a student's test. The student's answer is represented as a grid. "
        "In the grid, the left side contains the question numbers (e.g., 1, 2, 3), "
        "and the top contains the answer positions "
        "(e.g., A, B, C, etc.).\n"
        "Please identify the cells in the student's answer grid that are filled or marked "
        "(e.g., with an 'X', checkmark, or any other mark). "
        "For each question, list the answer positions that are selected.\n"
        "The response should be a dictionary where the key is the question number (integer), "
        "and the value is a list of answer positions "
        "(letters converted to integers, for example A is 1, B is 2, C is 3, etc). "
        "If multiple answers are chosen for a question, the list will contain multiple integers.\n"
        "Return only the raw (and valid) JSON dictionary in one line "
        "without any extra whitespace, formatting, or explanation.\n"
        'The dictionary format should be like this: {"1": [2], "2": [1, 3], "3": [3]}\n'
        "Ensure that all keys and values are integers, and values are lists of integers."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        n=1,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": student_answer.results_photo_url,
                        },
                    },
                ],
            }
        ],
    )
    response_message_content = response.choices[0].message.content.strip("json`")
    logger.info(f"Extracted such grid: {response_message_content}")
    return {int(key): value for key, value in json.loads(response_message_content).items()}
