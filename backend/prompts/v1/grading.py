from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionEvaluation(BaseModel):
    question_id: str
    marks_awarded: float
    max_marks: float
    is_correct: bool
    feedback: str = Field(description="Constructive pedagogical feedback on the student's answer")
    key_missed_concepts: List[str] = Field(default=[], description="Concepts or keywords missing from the student response")


class SubmissionEvaluationResult(BaseModel):
    total_marks_awarded: float
    total_max_marks: float
    percentage: float
    summary_feedback: str
    question_evaluations: List[QuestionEvaluation]


GRADING_PROMPT_TEMPLATE = """You are an objective academic evaluator. Grade the student's submission according to the question, model answer, and rubric.

Questions and Student Submissions:
{submissions_json}

Evaluation Rules:
1. Award partial credit fairly based on demonstrated understanding.
2. If the question is an exact MCQ and matches, award full marks.
3. For short answers, assess conceptual fidelity rather than exact wording match.
4. Provide constructive, encouraging, but rigorous feedback.
5. Output valid JSON adhering to the SubmissionEvaluationResult schema.
"""
