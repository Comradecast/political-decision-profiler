from typing import Dict, List
from src.schema.profile_schema import Values, DecisionBehavior, Contradiction

PAIR_MAGNITUDE_THRESHOLD = 0.6
PAIR_OPPOSITION_THRESHOLD = 0.45
GLOBAL_INCOHERENCE_THRESHOLD = 0.5

VECTOR_DIMENSIONS = [
    "market_preference",
    "decision_authority",
    "fairness_preference",
    "risk_tolerance",
    "time_horizon",
    "intervention_style",
    "system_trust",
]


def _to_normalized(value: float) -> float:
    return max(-1.0, min(1.0, (value - 50.0) / 50.0))


def profile_vector(values: Values, behavior: DecisionBehavior) -> Dict[str, float]:
    """Converts profile dimensions from [0, 100] scores into a [-1, 1] vector."""
    return {
        "market_preference": _to_normalized(values.market_preference),
        "decision_authority": _to_normalized(values.decision_authority),
        "fairness_preference": _to_normalized(values.fairness_preference),
        "risk_tolerance": _to_normalized(behavior.risk_tolerance),
        "time_horizon": _to_normalized(behavior.time_horizon),
        "intervention_style": _to_normalized(behavior.intervention_style),
        "system_trust": _to_normalized(behavior.system_trust.aggregate),
    }


class ContradictionEngine:
    """Detects cross-axis contradictions based on dimension interactions."""

    @staticmethod
    def detect(values: Values, behavior: DecisionBehavior) -> List[Contradiction]:
        contradictions = []
        vector = profile_vector(values, behavior)

        for index, first_dimension in enumerate(VECTOR_DIMENSIONS):
            for second_dimension in VECTOR_DIMENSIONS[index + 1:]:
                first_value = vector[first_dimension]
                second_value = vector[second_dimension]
                first_magnitude = abs(first_value)
                second_magnitude = abs(second_value)

                if (
                    first_magnitude >= PAIR_MAGNITUDE_THRESHOLD
                    and second_magnitude >= PAIR_MAGNITUDE_THRESHOLD
                    and first_value * second_value < 0.0
                ):
                    conflict_score = abs(first_value * second_value)
                    if conflict_score >= PAIR_OPPOSITION_THRESHOLD:
                        contradictions.append(Contradiction(
                            type="vector_opposition",
                            severity=round(min(1.0, conflict_score), 2),
                            description="Conflicting tendencies across dimensions",
                            related_dimensions=[first_dimension, second_dimension]
                        ))

        mean = sum(vector.values()) / len(vector)
        variance = sum((value - mean) ** 2 for value in vector.values()) / len(vector)
        if variance >= GLOBAL_INCOHERENCE_THRESHOLD:
            contradictions.append(Contradiction(
                type="profile_incoherence",
                severity=round(min(1.0, variance), 2),
                description="Conflicting tendencies across dimensions",
                related_dimensions=VECTOR_DIMENSIONS
            ))

        return contradictions
