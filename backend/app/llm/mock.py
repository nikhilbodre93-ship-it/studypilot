import asyncio
import json
import re
from typing import AsyncIterator, Optional, List, Dict, Any
from app.llm.base import BaseLLMProvider
from app.llm.tutor_knowledge import (
    generate_tutor_response,
    get_quiz_question_for_topic,
    KNOWLEDGE_BASE,
    find_matching_concept,
)


def _extract_topic_and_subject(prompt: str) -> tuple[str, str]:
    """Extract topic and subject name from LLM prompt templates."""
    topic = "Core Concepts"
    subject = "General Studies"

    # Search for Topic:, topic_name:, notes on:, etc.
    t_match = re.search(r"(?:topic|topic_name|notes\s+for\s+the\s+topic|notes\s+on):\s*([^\n\r,]+)", prompt, re.IGNORECASE)
    if t_match:
        topic = t_match.group(1).strip().strip("'\".").strip()

    # Search for Subject: or subject_name:
    s_match = re.search(r"(?:subject|subject_name):\s*([^\n\r,]+)", prompt, re.IGNORECASE)
    if s_match:
        subject = s_match.group(1).strip().strip("'\".").strip()

    return topic, subject


def _build_mock_notes(prompt: str) -> Dict[str, Any]:
    topic, subject = _extract_topic_and_subject(prompt)
    match = find_matching_concept(prompt, topic)

    if match:
        _, data = match
        title = f"Comprehensive Study Notes: {data['title']}"
        summary = data["summary"]
        sections = []
        for i, (heading, content) in enumerate(data["steps"], 1):
            sections.append({
                "heading": f"{i}. {heading.replace('*', '')}",
                "content_markdown": f"{content}\n\n**Intuitive Insight:** {data['analogy']}",
                "key_takeaways": [
                    f"Core mechanism: {heading.replace('*', '')}",
                    data["exam_traps"]
                ]
            })
        sections.append({
            "heading": f"{len(data['steps']) + 1}. Advanced Academic Rigor & Exam Traps",
            "content_markdown": f"{data['deeper_details']}\n\n**Critical Pitfall ⚠️:** {data['exam_traps']}",
            "key_takeaways": [
                data["exam_traps"],
                f"Verify understanding: {data['check_q']}"
            ]
        })
        return {
            "title": title,
            "summary": summary,
            "sections": sections,
            "citations": [f"Curriculum Reference: {data['title']}", "Standard Academic Syllabus"],
            "not_in_context_warning": None
        }

    # Dynamic fallback based on topic and subject
    return {
        "title": f"Study Notes: {topic} ({subject})",
        "summary": f"A comprehensive academic overview of {topic} within {subject}, detailing core principles, operational frameworks, and critical exam problem-solving strategies.",
        "sections": [
            {
                "heading": f"1. Foundations & Definitions of {topic}",
                "content_markdown": f"**{topic}** forms a foundational pillar in **{subject}**. The core architecture establishes systematic rules governing component interactions and reliable execution.\n\n- Primary objective: Maximize efficiency while maintaining strict consistency.\n- Essential prerequisites: Understanding foundational concepts and boundary constraints.",
                "key_takeaways": [
                    f"Master the formal definition of {topic}",
                    "Identify key operational constraints early in problem-solving"
                ]
            },
            {
                "heading": f"2. Mechanistic Architecture & Data Flow",
                "content_markdown": f"When analyzing {topic}, processes proceed through structured sequential stages:\n1. **Initialization**: Input parameters and boundary criteria are established.\n2. **Transformation**: Core operations modify and optimize internal state.\n3. **Termination & Output**: Reliable results are produced with verifiable consistency.",
                "key_takeaways": [
                    "Trace inputs systematically through every stage",
                    "Verify state invariants at each transformation point"
                ]
            },
            {
                "heading": f"3. Exam Problem-Solving & High-Yield Pitfalls",
                "content_markdown": f"Common errors encountered when testing on {topic} include:\n- Failing to check edge cases and boundary limits.\n- Confusing primary causes with observable secondary effects.\n- Over-simplifying multi-step derivations without documenting intermediate logic.",
                "key_takeaways": [
                    "Always state governing assumptions before calculating",
                    "Document step-by-step reasoning for full partial credit"
                ]
            }
        ],
        "citations": [f"Syllabus: {subject} - {topic}", "Core Textbook Chapter Reference"],
        "not_in_context_warning": None
    }


def _build_mock_flashcards(prompt: str) -> Dict[str, Any]:
    topic, subject = _extract_topic_and_subject(prompt)
    match = find_matching_concept(prompt, topic)

    if match:
        _, data = match
        cards = []
        for heading, content in data["steps"][:4]:
            cards.append({
                "front": f"Explain the role of {heading.replace('*', '')} in {data['title']}.",
                "back": content,
                "explanation": data["analogy"],
                "difficulty": "medium",
                "citation": f"{data['title']} Reference"
            })
        cards.append({
            "front": f"What is a critical exam trap when solving problems in {data['title']}?",
            "back": data["exam_traps"],
            "explanation": data["deeper_details"],
            "difficulty": "hard",
            "citation": "Exam Strategy Guide"
        })
        cards.append({
            "front": data["check_q"],
            "back": "Refer to the core working principle: Verify all boundary conditions and formal definitions.",
            "explanation": "Self-assessment recall challenge.",
            "difficulty": "easy",
            "citation": "Review Checklist"
        })
        return {
            "deck_title": f"{data['title']} High-Yield Deck",
            "topic_name": topic,
            "cards": cards,
            "not_in_context_warning": None
        }

    # Dynamic fallback flashcards
    return {
        "deck_title": f"{topic} Mastery Deck",
        "topic_name": topic,
        "cards": [
            {
                "front": f"What is the core definition and purpose of {topic}?",
                "back": f"{topic} defines the structured mechanism and operational rules that govern system behavior in {subject}.",
                "explanation": "Fundamental baseline concept for all exam questions.",
                "difficulty": "easy",
                "citation": f"Curriculum: {subject}"
            },
            {
                "front": f"What are the key working principles behind {topic}?",
                "back": "Input validation, structured state transformation, and guaranteed output consistency under defined constraints.",
                "explanation": "Step-by-step workflow architecture.",
                "difficulty": "medium",
                "citation": "Lecture Notes"
            },
            {
                "front": f"What is the most frequent student pitfall when solving questions on {topic}?",
                "back": "Failing to check boundary limits, assuming constant parameters without validation, and confusing symptoms with root causes.",
                "explanation": "High-yield exam avoidance tip.",
                "difficulty": "hard",
                "citation": "Exam Rubric"
            },
            {
                "front": f"How does {topic} connect to practical applications in {subject}?",
                "back": f"It serves as a modular building block enabling reliable, scalable problem-solving across advanced {subject} systems.",
                "explanation": "Practical implementation rationale.",
                "difficulty": "medium",
                "citation": "Application Guide"
            }
        ],
        "not_in_context_warning": None
    }


def _build_mock_question_paper(prompt: str) -> Dict[str, Any]:
    topic, subject = _extract_topic_and_subject(prompt)
    match = find_matching_concept(prompt, topic or subject)

    if match:
        _, data = match
        q1_text = data["check_q"]
        q2_text = f"Explain the mechanism of {data['steps'][0][0].replace('*', '')} in detail."
        q3_text = f"Analyze {data['title']}, discuss its intuitive analogy, and evaluate how to avoid common exam pitfalls."
    else:
        q1_text = f"Which statement best describes the fundamental principle of {subject} - {topic}?"
        q2_text = f"Outline the core working mechanism of {topic} and explain its practical significance in {subject}."
        q3_text = f"Provide a comprehensive analytical breakdown of {topic}. Detail its operational architecture, derive key relationships, and evaluate boundary conditions."

    return {
        "title": f"Comprehensive {subject} Examination",
        "subject_name": subject,
        "total_marks": 100,
        "duration_minutes": 60,
        "instructions": [
            "Answer all questions in Section A (Objective Conceptual).",
            "Section B contains short analytical explanations (5 marks each).",
            "Section C requires extended problem solving and derivations (10 marks each)."
        ],
        "sections": [
            {
                "name": "Section A: Objective Knowledge",
                "description": "Foundational conceptual multiple choice questions",
                "section_code": "A",
                "total_marks": 20,
                "questions": [
                    {
                        "id": "Q1",
                        "section": "A",
                        "question_text": q1_text,
                        "marks": 2,
                        "options": [
                            "Understanding the core mechanism and its structural relationships",
                            "Ignoring boundary conditions and relying on intuition",
                            "Assuming all real-world variables remain invariant",
                            "Omitting units and mathematical checks"
                        ],
                        "model_answer": "Understanding the core mechanism and its structural relationships",
                        "rubric": "2 marks for identifying the correct fundamental principle."
                    }
                ]
            },
            {
                "name": "Section B: Conceptual Clarification",
                "description": "Concise structured scientific and technical explanations",
                "section_code": "B",
                "total_marks": 30,
                "questions": [
                    {
                        "id": "Q2",
                        "section": "B",
                        "question_text": q2_text,
                        "marks": 5,
                        "options": None,
                        "model_answer": f"Clear explanation of the core principles governing {topic}, detailing inputs, transformations, and output consistency.",
                        "rubric": "2 marks for definition, 2 marks for mechanism description, 1 mark for practical example."
                    }
                ]
            },
            {
                "name": "Section C: Analytical Inquiry",
                "description": "Comprehensive long-form problem solving and synthesis",
                "section_code": "C",
                "total_marks": 50,
                "questions": [
                    {
                        "id": "Q3",
                        "section": "C",
                        "question_text": q3_text,
                        "marks": 10,
                        "options": None,
                        "model_answer": f"In-depth analysis establishing theoretical background, stepwise operational dynamics, edge cases, and real-world implementation.",
                        "rubric": "4 marks for theoretical framework, 4 marks for mathematical/technical rigor, 2 marks for boundary analysis."
                    }
                ]
            }
        ]
    }


def _build_mock_roadmap(prompt: str) -> Dict[str, Any]:
    topic, subject = _extract_topic_and_subject(prompt)

    return {
        "title": f"Strategic Revision Roadmap: {subject}",
        "subject_name": subject,
        "total_estimated_hours": 20,
        "phases": [
            {
                "phase_number": 1,
                "name": f"Phase 1: Foundations & Core Concepts of {subject}",
                "timeframe": "Week 1",
                "summary": f"Build solid conceptual grounding in {topic} and fundamental principles.",
                "tasks": [
                    {
                        "id": "task-1",
                        "title": f"Review foundational lecture notes on {topic}",
                        "topic_name": topic,
                        "task_type": "learn",
                        "estimated_minutes": 35,
                        "completed": False
                    },
                    {
                        "id": "task-2",
                        "title": f"Diagnostic quiz on {topic} definitions & rules",
                        "topic_name": topic,
                        "task_type": "quiz",
                        "estimated_minutes": 20,
                        "completed": False
                    }
                ]
            },
            {
                "phase_number": 2,
                "name": f"Phase 2: Deep Mechanics & Problem Solving",
                "timeframe": "Week 2",
                "summary": "Master multi-step operations, formulas, and structural relationships.",
                "tasks": [
                    {
                        "id": "task-3",
                        "title": f"Work through step-by-step practice problems for {topic}",
                        "topic_name": topic,
                        "task_type": "learn",
                        "estimated_minutes": 45,
                        "completed": False
                    },
                    {
                        "id": "task-4",
                        "title": f"Active spaced flashcard recall for {subject}",
                        "topic_name": topic,
                        "task_type": "review",
                        "estimated_minutes": 25,
                        "completed": False
                    }
                ]
            },
            {
                "phase_number": 3,
                "name": f"Phase 3: High-Yield Exam Preparation",
                "timeframe": "Week 3",
                "summary": "Target high-yield exam pitfalls, edge cases, and past question papers.",
                "tasks": [
                    {
                        "id": "task-5",
                        "title": f"Timed mock exam paper for {subject}",
                        "topic_name": topic,
                        "task_type": "quiz",
                        "estimated_minutes": 60,
                        "completed": False
                    }
                ]
            }
        ],
        "not_in_context_warning": None
    }


class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock LLM provider for local dev and automated test suites."""

    def __init__(self, model_name: str = "mock-model"):
        super().__init__(model_name=model_name, provider_name="mock")

    async def _raw_completion(self, system_prompt: str, prompt: str, json_mode: bool = False) -> str:
        # Determine schema by checking schema name in system_prompt
        if "GeneratedNotes" in system_prompt:
            return json.dumps(_build_mock_notes(prompt))

        elif "GeneratedQuiz" in system_prompt:
            topic, _ = _extract_topic_and_subject(prompt)
            q_primary = get_quiz_question_for_topic(f"{prompt} {topic}")
            questions_list = [
                {
                    "question_text": q_primary["question_text"],
                    "question_type": "multiple_choice",
                    "options": q_primary["options"] or ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": q_primary["correct_answer"],
                    "explanation": q_primary["explanation"],
                    "difficulty": "medium",
                    "citation": q_primary.get("citation", "Curriculum Reference")
                }
            ]
            if "count=1" not in prompt and "count: 1" not in prompt:
                questions_list.extend([
                    {
                        "question_text": f"True or False: Fundamental mechanisms in {topic} follow reproducible physical, biological, or computational laws.",
                        "question_type": "true_false",
                        "options": ["True", "False"],
                        "correct_answer": "True",
                        "explanation": "Academic and engineering systems operate according to verifiable, reproducible principles.",
                        "difficulty": "easy",
                        "citation": "Core Textbook"
                    },
                    {
                        "question_text": f"Explain why understanding the core principle of {topic} is essential for solving complex exam problems.",
                        "question_type": "short_answer",
                        "options": None,
                        "correct_answer": "It provides the foundational framework needed to analyze variations, calculate outcomes, and avoid common traps.",
                        "explanation": "Conceptual comprehension prevents reliance on rote memorization.",
                        "difficulty": "medium",
                        "citation": "Syllabus Guide"
                    }
                ])

            return json.dumps({
                "title": f"Mastery Assessment: {topic}",
                "topic_name": topic,
                "questions": questions_list,
                "not_in_context_warning": None
            })

        elif "GeneratedFlashcardDeck" in system_prompt:
            return json.dumps(_build_mock_flashcards(prompt))

        elif "GeneratedQuestionPaper" in system_prompt:
            return json.dumps(_build_mock_question_paper(prompt))

        elif "GeneratedRoadmap" in system_prompt:
            return json.dumps(_build_mock_roadmap(prompt))

        elif "SubmissionEvaluationResult" in system_prompt:
            return json.dumps({
                "total_marks_awarded": 14.0,
                "total_max_marks": 17.0,
                "percentage": 82.4,
                "summary_feedback": "Strong conceptual comprehension demonstrated across objective and descriptive questions. Clear explanation of core mechanisms.",
                "question_evaluations": [
                    {
                        "question_id": "Q1",
                        "marks_awarded": 2.0,
                        "max_marks": 2.0,
                        "is_correct": True,
                        "feedback": "Accurately identified the core principle.",
                        "key_missed_concepts": []
                    },
                    {
                        "question_id": "Q2",
                        "marks_awarded": 4.0,
                        "max_marks": 5.0,
                        "is_correct": True,
                        "feedback": "Correctly linked operational dynamics to output outcomes, with minor omissions in edge case handling.",
                        "key_missed_concepts": ["boundary verification"]
                    },
                    {
                        "question_id": "Q3",
                        "marks_awarded": 8.0,
                        "max_marks": 10.0,
                        "is_correct": True,
                        "feedback": "Clear explanation of architectural framework and error avoidance.",
                        "key_missed_concepts": ["quantitative bounds"]
                    }
                ]
            })

        # Generic default JSON response
        return json.dumps({"response": "Mock LLM output generated successfully.", "status": "ok"})

    async def generate_stream(
        self,
        system_prompt: str,
        prompt: str,
        user_id: Optional[int] = None,
        feature_name: str = "tutor",
        history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterator[str]:
        # Extract topic name from system_prompt if available
        topic_name = "Core Concepts"
        if "topic:" in system_prompt.lower():
            topic_match = re.search(r"topic:\s*'([^']+)'", system_prompt, re.IGNORECASE)
            if topic_match:
                topic_name = topic_match.group(1)

        # Detect tutoring mode from system_prompt
        mode = "standard"
        if "ELI5" in system_prompt:
            mode = "eli5"
        elif "Deep Dive" in system_prompt:
            mode = "deeper"

        # Check for grounding context in system_prompt
        context_str = ""
        if "<STUDY_MATERIAL_CONTEXT>" in system_prompt:
            start_tag = "<STUDY_MATERIAL_CONTEXT>"
            end_tag = "</STUDY_MATERIAL_CONTEXT>"
            start_idx = system_prompt.find(start_tag)
            end_idx = system_prompt.find(end_tag)
            if start_idx != -1 and end_idx != -1:
                context_str = system_prompt[start_idx + len(start_tag):end_idx].strip()

        # Generate authentic, educational, rigorous response
        response_text = generate_tutor_response(
            prompt=prompt,
            topic_name=topic_name,
            mode=mode,
            context=context_str,
            history=history
        )

        words = response_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            yield chunk
            await asyncio.sleep(0.015)

        await self.log_usage(
            user_id=user_id,
            feature_name=feature_name,
            prompt_tokens=max(1, len(prompt) // 4),
            completion_tokens=len(words)
        )
