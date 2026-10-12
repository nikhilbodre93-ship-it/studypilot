from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    question_text: str = Field(description="Clear, unambiguous question stem")
    question_type: Literal["multiple_choice", "true_false", "short_answer"] = Field(description="Question format")
    options: Optional[List[str]] = Field(default=None, description="Array of 4 options for multiple_choice, or None for short_answer")
    correct_answer: str = Field(description="The correct answer string, option text, or model short answer")
    explanation: str = Field(description="Step-by-step pedagogical explanation of why this is correct and why other options are wrong")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium")
    citation: Optional[str] = Field(default=None, description="Section or page citation grounded in the source material")


class GeneratedQuiz(BaseModel):
    title: str = Field(description="Quiz title")
    topic_name: str
    questions: List[QuestionItem] = Field(description="List of practice questions")
    not_in_context_warning: Optional[str] = None


QUIZ_PROMPT_TEMPLATE = """Create a practice quiz of {count} questions for topic: "{topic_name}".
Difficulty: {difficulty}
Question Types to include: {question_types}

<STUDY_MATERIAL_CONTEXT>
{context}
</STUDY_MATERIAL_CONTEXT>

Requirements:
1. For multiple_choice, provide 4 plausible options with exactly 1 correct answer.
2. For true_false, options should be ["True", "False"].
3. For short_answer, provide an exact model answer in correct_answer.
4. Ground every question strictly in the provided study material.
5. Provide detailed pedagogical explanations for every question.
6. Output valid JSON adhering strictly to the GeneratedQuiz schema.
"""
