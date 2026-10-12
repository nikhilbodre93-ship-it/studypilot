from typing import List, Optional
from pydantic import BaseModel, Field


class NoteSection(BaseModel):
    heading: str = Field(description="Section heading")
    content_markdown: str = Field(description="Detailed educational content with markdown formatting and bullet points")
    key_takeaways: List[str] = Field(description="High-yield exam takeaways")


class GeneratedNotes(BaseModel):
    title: str = Field(description="Clean, descriptive title for the study note")
    summary: str = Field(description="2-3 sentence executive summary of the topic")
    sections: List[NoteSection] = Field(description="Structured thematic sections")
    citations: List[str] = Field(default=[], description="Source chunk or document references")
    not_in_context_warning: Optional[str] = Field(default=None, description="Explicit warning if context lacked required details")


NOTES_PROMPT_TEMPLATE = """Generate comprehensive, clear, high-yield study notes for the topic: "{topic_name}".
Academic Level: {level}

<STUDY_MATERIAL_CONTEXT>
{context}
</STUDY_MATERIAL_CONTEXT>

Format requirements:
- Produce clear Markdown formatting with headings, bullet points, bold key terms, and formulas where applicable.
- Extract high-yield takeaways that commonly appear on exams.
- Ground the content strictly in the study material. If details are missing from the context, note them in 'not_in_context_warning'.
- Output strictly in valid JSON adhering to the GeneratedNotes schema.
"""
