from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class FlashcardItem(BaseModel):
    front: str = Field(description="Front of card: targeted concept, prompt, or question")
    back: str = Field(description="Back of card: concise, memorable explanation or definition")
    explanation: Optional[str] = Field(default=None, description="Additional context or memory mnemonic")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium")
    citation: Optional[str] = Field(default=None, description="Page or chunk citation")


class GeneratedFlashcardDeck(BaseModel):
    deck_title: str
    topic_name: str
    cards: List[FlashcardItem]
    not_in_context_warning: Optional[str] = None


FLASHCARD_PROMPT_TEMPLATE = """Generate a high-yield spaced repetition flashcard deck for topic: "{topic_name}".
Number of cards: {count}

<STUDY_MATERIAL_CONTEXT>
{context}
</STUDY_MATERIAL_CONTEXT>

Guidelines:
1. Ensure the front contains a single clear concept or query (atomic flashcards are best for memory).
2. Ensure the back is concise, precise, and easily testable.
3. Ground the concepts directly in the study material.
4. Output valid JSON adhering strictly to the GeneratedFlashcardDeck schema.
"""
