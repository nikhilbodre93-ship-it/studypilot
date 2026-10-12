from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class RoadmapTask(BaseModel):
    id: str = Field(description="Unique task identifier, e.g. task-1")
    title: str = Field(description="Actionable task title")
    topic_name: str = Field(description="Associated syllabus topic")
    task_type: Literal["learn", "review", "quiz", "practice"] = Field(default="learn")
    estimated_minutes: int = Field(default=30)
    completed: bool = Field(default=False)


class RoadmapPhase(BaseModel):
    phase_number: int = Field(description="1, 2, 3, etc.")
    name: str = Field(description="e.g. Phase 1: Core Fundamentals")
    timeframe: str = Field(description="e.g. Week 1-2")
    summary: str = Field(description="Strategic learning objectives for this phase")
    tasks: List[RoadmapTask]


class GeneratedRoadmap(BaseModel):
    title: str = Field(description="Roadmap title")
    subject_name: str
    total_estimated_hours: int = Field(default=20)
    phases: List[RoadmapPhase]
    not_in_context_warning: Optional[str] = None


ROADMAP_PROMPT_TEMPLATE = """You are creating a comprehensive, phased learning roadmap for subject: "{subject_name}".
Target Exam Date: {exam_date}
Topics in syllabus:
{topics_summary}

Student Current Mastery Profile:
{mastery_profile}

<STUDY_MATERIAL_CONTEXT>
{context}
</STUDY_MATERIAL_CONTEXT>

Guidelines:
1. Structure the syllabus into logical chronological phases (e.g. Phase 1: Core Fundamentals, Phase 2: Advanced Applications, Phase 3: Final Mock Revision).
2. Prioritize weaker topics (lower mastery) earlier in the sequence.
3. Provide actionable concrete tasks (learn, review, quiz, practice) with estimated minutes.
4. Output strictly valid JSON adhering to the GeneratedRoadmap schema.
"""
