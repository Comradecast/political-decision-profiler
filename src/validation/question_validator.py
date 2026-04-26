import re
from src.schema.question_schema import Question

class QuestionValidator:
    """Validates questions against strict design rules."""

    @staticmethod
    def validate(question: Question) -> bool:
        # 1. tradeoff_present must be true
        if not question.tradeoff_present:
            raise ValueError("Invalid Question: tradeoff_present must be True.")

        # Reject obvious no-signal questions
        effects = [opt.scoring_effects for opt in question.options]
        if all(e == effects[0] for e in effects):
            raise ValueError("Invalid Question: No signal (all options have identical scoring_effects).")

        full_text = f"{question.scenario} " + " ".join(opt.label for opt in question.options)
        text_lower = full_text.lower()

        primary = question.primary_dimension

        # Enforce dimension isolation & required primary keys
        for opt in question.options:
            keys = list(opt.scoring_effects.keys())
            if len(keys) > 2:
                raise ValueError("Invalid Question: Option has more than 2 scoring dimensions.")
            
            if primary == "system_trust":
                has_gov = "system_trust_government" in keys
                has_corp = "system_trust_corporate" in keys
                if not (has_gov or has_corp):
                    raise ValueError("Invalid Question: System Trust option must include a system_trust scoring key.")
                for k in keys:
                    if k not in ["system_trust_government", "system_trust_corporate"]:
                        raise ValueError(f"Invalid Question: System Trust questions cannot score other dimensions (found {k}).")
            else:
                if primary not in keys:
                    raise ValueError(f"Invalid Question: Option missing primary dimension '{primary}' in scoring_effects.")

        # Dimension-specific rules
        if primary == "risk_tolerance":
            if question.uncertainty_present:
                raise ValueError("Invalid Question: Risk Tolerance questions must have uncertainty_present=False.")

        elif primary == "intervention_style":
            if not question.uncertainty_present:
                raise ValueError("Invalid Question: Intervention Style questions must have uncertainty_present=True.")
            
            uncertainty_keywords = ["may", "might", "possible", "uncertain"]
            if not any(word in text_lower for word in uncertainty_keywords):
                raise ValueError("Invalid Question: Intervention Style scenario lacks uncertainty keywords.")

        elif primary == "time_horizon":
            time_words = ["now", "immediate", "short-term", "present", "delay", "future", "long-term", "later", "wait", "cost"]
            if not any(word in text_lower for word in time_words):
                raise ValueError("Invalid Question: Time Horizon questions must imply present cost vs delayed benefit.")

        elif primary == "system_trust":
            belief_words = ["believe", "think", "trust"]
            if not any(word in text_lower for word in belief_words):
                raise ValueError("Invalid Question: System Trust questions must use belief framing.")

        return True
