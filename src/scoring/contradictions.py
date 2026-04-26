from typing import Dict, List, Literal, TypedDict
from src.schema.profile_schema import Values, DecisionBehavior, Contradiction

Alignment = Literal["same_direction", "opposite_direction", "independent"]

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


class Relationship(TypedDict):
    first_dimension: str
    second_dimension: str
    expected_alignment: Alignment
    weight: float
    description: str


# Model policy: this relationship matrix defines which dimensions should be
# checked together. It is intentionally explicit and can evolve as the profiler
# model matures.
RELATIONSHIPS: List[Relationship] = [
    {
        "first_dimension": "market_preference",
        "second_dimension": "risk_tolerance",
        "expected_alignment": "same_direction",
        "weight": 0.8,
        "description": "Market preference and risk tolerance usually move together",
    },
    {
        "first_dimension": "decision_authority",
        "second_dimension": "intervention_style",
        "expected_alignment": "same_direction",
        "weight": 0.8,
        "description": "Decision authority and intervention style usually move together",
    },
    {
        "first_dimension": "time_horizon",
        "second_dimension": "intervention_style",
        "expected_alignment": "same_direction",
        "weight": 0.7,
        "description": "Time horizon and intervention style usually move together",
    },
    {
        "first_dimension": "market_preference",
        "second_dimension": "intervention_style",
        "expected_alignment": "opposite_direction",
        "weight": 1.0,
        "description": "Market preference and intervention style usually pull in opposite directions",
    },
    {
        "first_dimension": "decision_authority",
        "second_dimension": "system_trust",
        "expected_alignment": "opposite_direction",
        "weight": 0.8,
        "description": "Decision authority and system trust usually pull in opposite directions",
    },
    {
        "first_dimension": "market_preference",
        "second_dimension": "time_horizon",
        "expected_alignment": "independent",
        "weight": 0.0,
        "description": "Market preference and time horizon are treated as independent",
    },
    {
        "first_dimension": "fairness_preference",
        "second_dimension": "system_trust",
        "expected_alignment": "independent",
        "weight": 0.0,
        "description": "Fairness preference and system trust are treated as independent",
    },
    {
        "first_dimension": "fairness_preference",
        "second_dimension": "risk_tolerance",
        "expected_alignment": "independent",
        "weight": 0.0,
        "description": "Fairness preference and risk tolerance are treated as independent",
    },
]


def _pair_key(first_dimension: str, second_dimension: str) -> tuple[str, str]:
    return tuple(sorted([first_dimension, second_dimension]))


RELATIONSHIP_MATRIX = {
    _pair_key(relationship["first_dimension"], relationship["second_dimension"]): relationship
    for relationship in RELATIONSHIPS
}


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


def _get_relationship(first_dimension: str, second_dimension: str) -> Relationship:
    return RELATIONSHIP_MATRIX.get(
        _pair_key(first_dimension, second_dimension),
        {
            "first_dimension": first_dimension,
            "second_dimension": second_dimension,
            "expected_alignment": "independent",
            "weight": 0.0,
            "description": "Dimensions are treated as independent",
        }
    )


def _has_relationship_conflict(first_value: float, second_value: float, alignment: Alignment) -> bool:
    if alignment == "same_direction":
        return first_value * second_value < 0.0
    if alignment == "opposite_direction":
        return first_value * second_value > 0.0
    return False


class ContradictionEngine:
    """Detects cross-axis contradictions based on dimension interactions."""

    @staticmethod
    def detect(values: Values, behavior: DecisionBehavior) -> List[Contradiction]:
        contradictions = []
        vector = profile_vector(values, behavior)
        seen_pairs = set()

        for index, first_dimension in enumerate(VECTOR_DIMENSIONS):
            for second_dimension in VECTOR_DIMENSIONS[index + 1:]:
                pair_key = _pair_key(first_dimension, second_dimension)
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                relationship = _get_relationship(first_dimension, second_dimension)
                alignment = relationship["expected_alignment"]
                if alignment == "independent":
                    continue

                first_value = vector[first_dimension]
                second_value = vector[second_dimension]
                first_magnitude = abs(first_value)
                second_magnitude = abs(second_value)

                if (
                    first_magnitude >= PAIR_MAGNITUDE_THRESHOLD
                    and second_magnitude >= PAIR_MAGNITUDE_THRESHOLD
                    and _has_relationship_conflict(first_value, second_value, alignment)
                ):
                    severity = abs(first_value * second_value) * relationship["weight"]
                    severity = min(1.0, severity)
                    if severity >= PAIR_OPPOSITION_THRESHOLD:
                        contradictions.append(Contradiction(
                            type="relationship_conflict",
                            severity=round(severity, 2),
                            description=relationship["description"],
                            related_dimensions=[first_dimension, second_dimension]
                        ))

        mean = sum(vector.values()) / len(vector)
        variance = sum((value - mean) ** 2 for value in vector.values()) / len(vector)
        if variance >= GLOBAL_INCOHERENCE_THRESHOLD:
            sorted_dimensions = sorted(
                vector.items(),
                key=lambda item: abs(item[1] - mean),
                reverse=True
            )
            top_dimensions = [dimension for dimension, _ in sorted_dimensions[:3]]
            contradictions.append(Contradiction(
                type="profile_incoherence",
                severity=round(min(1.0, variance * 2.0), 2),
                description="Conflicting tendencies across dimensions",
                related_dimensions=top_dimensions
            ))

        return contradictions
