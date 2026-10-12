from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class PaperQuestion(BaseModel):
    id: str = Field(description="Unique question identifier, e.g. Q1, Q2")
    section: Literal["A", "B", "C"] = Field(description="Exam section")
    question_text: str = Field(description="Question text")
    marks: int = Field(description="Allocated marks for this question")
    options: Optional[List[str]] = Field(default=None, description="Options for Section A MCQs")
    model_answer: str = Field(description="Complete answer key / grading criteria")
    rubric: Optional[str] = Field(default=None, description="Marking rubric breakdown")


class PaperSection(BaseModel):
    name: str = Field(description="e.g. Section A: Objective & Conceptual Foundations")
    description: str
    section_code: Literal["A", "B", "C"]
    total_marks: int
    questions: List[PaperQuestion]


class GeneratedQuestionPaper(BaseModel):
    title: str = Field(description="e.g. Molecular Biology Comprehensive Mock Exam")
    subject_name: str
    total_marks: int = Field(default=100)
    duration_minutes: int = Field(default=60)
    instructions: List[str]
    sections: List[PaperSection]


QUESTION_PAPER_PROMPT_TEMPLATE = """Create an authentic, rigorous exam question paper for subject: "{subject_name}".
Topics covered: {topics_list}
Target Total Marks: {total_marks}
Exam Duration: {duration_minutes} minutes

Format Requirements:
1. Section A: Objective & Multiple Choice (e.g. 1-2 marks each)
2. Section B: Short Answer & Concept Elaboration (e.g. 5 marks each)
3. Section C: Comprehensive Problem Solving & Analytical Inquiry (e.g. 10 marks each)
4. Include a detailed model_answer and marking rubric for every single question.
5. Ground questions in the provided context:

<STUDY_MATERIAL_CONTEXT>
{context}
</STUDY_MATERIAL_CONTEXT>

Output strictly in valid JSON adhering to the GeneratedQuestionPaper schema.
"""
