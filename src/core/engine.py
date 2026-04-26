from typing import List, Tuple
from src.schema.question_schema import Question
from src.schema.profile_schema import Profile, Metadata
from src.validation.question_validator import QuestionValidator
from src.scoring.scorer import Scorer
from src.scoring.contradictions import ContradictionEngine

class ProfilerEngine:
    """Orchestrates the validation, scoring, and profile generation."""

    def __init__(self):
        self.scorer = Scorer()
        self.total_questions = 0
        self.neutral_answers = 0

    def process_responses(self, questions_and_answers: List[Tuple[Question, str]]) -> Profile:
        """
        Accepts validated questions and selected responses.
        Generates the final profile.
        """
        self.scorer = Scorer()
        self.total_questions = 0
        self.neutral_answers = 0

        seen_question_ids = set()
        for question, _ in questions_and_answers:
            if question.id in seen_question_ids:
                raise ValueError(f"Duplicate question id in responses: {question.id}")
            seen_question_ids.add(question.id)

        for question, answer_id in questions_and_answers:
            # 1. Validate Question
            QuestionValidator.validate(question)
            
            # 2. Score Response
            self.scorer.process_response(question, answer_id)
            
            # 3. Track metadata
            self.total_questions += 1
            
            # Provisional: future schemas should explicitly mark neutral options.
            selected_option = next(opt for opt in question.options if opt.id == answer_id)
            is_neutral = all(abs(effect) < 1e-6 for effect in selected_option.scoring_effects.values())
            if is_neutral:
                self.neutral_answers += 1

        # 4. Generate Core Structures
        values = self.scorer.get_values()
        behavior = self.scorer.get_decision_behavior()
        cube = self.scorer.get_cube_position()
        
        # 5. Detect Contradictions
        contradictions = ContradictionEngine.detect(values, behavior)
        
        # 6. Calculate Metadata
        # Confidence: decisiveness
        confidence = 0.0
        if self.total_questions > 0:
            confidence = 1.0 - (self.neutral_answers / self.total_questions)
            
        # Consistency: internal coherence
        consistency = 1.0
        if contradictions:
            avg_severity = sum(c.severity for c in contradictions) / len(contradictions)
            consistency = 1.0 - avg_severity

        metadata = Metadata(
            confidence_score=round(confidence, 2),
            consistency_score=round(consistency, 2)
        )
        
        # Assemble Final Profile
        return Profile(
            values=values,
            decision_behavior=behavior,
            cube_position=cube,
            metadata=metadata,
            contradictions=contradictions,
            insights=[] # To be populated by an insight engine later if needed
        )
