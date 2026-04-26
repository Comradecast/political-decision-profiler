from typing import Dict, List
from src.schema.question_schema import Question, DimensionKey
from src.schema.profile_schema import Values, DecisionBehavior, SystemTrust, CubePosition

class Scorer:
    """Computes final scores from question responses."""

    def __init__(self):
        self.raw_scores: Dict[DimensionKey, float] = {
            "market_preference": 0.0,
            "decision_authority": 0.0,
            "fairness_preference": 0.0,
            "risk_tolerance": 0.0,
            "time_horizon": 0.0,
            "intervention_style": 0.0,
            "system_trust_government": 0.0,
            "system_trust_corporate": 0.0,
        }
        self.counts: Dict[DimensionKey, int] = {k: 0 for k in self.raw_scores}

    def process_response(self, question: Question, selected_option_id: str) -> None:
        """Processes a single response and updates raw scores."""
        selected_option = next((opt for opt in question.options if opt.id == selected_option_id), None)
        if not selected_option:
            raise ValueError(f"Option ID {selected_option_id} not found in question {question.id}")

        for dim, effect in selected_option.scoring_effects.items():
            self.raw_scores[dim] += effect
            self.counts[dim] += 1

    def _normalize(self, raw_score: float, count: int) -> float:
        """Normalizes a raw score to a 0-100 range."""
        if count == 0:
            return 50.0  # Default neutral
        
        # Max theoretical score per dimension per question is 100
        # Min theoretical score is -100
        # If max_possible was count * 100:
        # Score ranges from [-100*count, 100*count].
        # Map [-100*count, 100*count] -> [0, 100]
        max_possible = count * 100.0
        normalized = ((raw_score + max_possible) / (2 * max_possible)) * 100.0
        return max(0.0, min(100.0, normalized))

    def get_values(self) -> Values:
        return Values(
            market_preference=self._normalize(self.raw_scores["market_preference"], self.counts["market_preference"]),
            decision_authority=self._normalize(self.raw_scores["decision_authority"], self.counts["decision_authority"]),
            fairness_preference=self._normalize(self.raw_scores["fairness_preference"], self.counts["fairness_preference"])
        )

    def get_system_trust(self) -> SystemTrust:
        gov = self._normalize(self.raw_scores["system_trust_government"], self.counts["system_trust_government"])
        corp = self._normalize(self.raw_scores["system_trust_corporate"], self.counts["system_trust_corporate"])
        
        aggregate = (gov + corp) / 2.0
        variance = abs(gov - corp)
        
        return SystemTrust(
            government=gov,
            corporate=corp,
            aggregate=aggregate,
            variance=variance
        )

    def get_decision_behavior(self) -> DecisionBehavior:
        return DecisionBehavior(
            risk_tolerance=self._normalize(self.raw_scores["risk_tolerance"], self.counts["risk_tolerance"]),
            time_horizon=self._normalize(self.raw_scores["time_horizon"], self.counts["time_horizon"]),
            intervention_style=self._normalize(self.raw_scores["intervention_style"], self.counts["intervention_style"]),
            system_trust=self.get_system_trust()
        )

    def get_cube_position(self) -> CubePosition:
        return CubePosition(
            x=self._normalize(self.raw_scores["market_preference"], self.counts["market_preference"]),
            y=self._normalize(self.raw_scores["decision_authority"], self.counts["decision_authority"]),
            z=self._normalize(self.raw_scores["risk_tolerance"], self.counts["risk_tolerance"])
        )
