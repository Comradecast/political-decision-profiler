from typing import List
from src.schema.profile_schema import Values, DecisionBehavior, Contradiction

class ContradictionEngine:
    """Detects cross-axis contradictions based on dimension interactions."""

    @staticmethod
    def detect(values: Values, behavior: DecisionBehavior) -> List[Contradiction]:
        contradictions = []

        # Current contradiction rules are provisional hand-authored heuristics;
        # later versions should use a more general dimension-space model.
        # Example Contradiction 1: Market preference vs Intervention style
        # Prefers market (high x) but supports early intervention (low intervention_style)
        market_pref = values.market_preference
        intervention = behavior.intervention_style
        
        # severity is how close they are to opposite extremes
        # If market_pref is 100, and intervention is 0 -> strong contradiction
        market_diff = market_pref - 50.0
        intervention_diff = 50.0 - intervention
        
        if market_diff > 10.0 and intervention_diff > 10.0:
            # Both are strongly in the contradictory direction
            # Max possible product of diffs is 50 * 50 = 2500
            severity = (market_diff * intervention_diff) / 2500.0
            if severity > 0.3:
                contradictions.append(Contradiction(
                    type="market_vs_intervention",
                    severity=round(severity, 2),
                    description="Prefers market outcomes but supports early intervention under uncertainty",
                    related_dimensions=["market_preference", "intervention_style"]
                ))
        
        # Example Contradiction 2: Decentralized Authority vs High System Trust (Government)
        # Prefers decentralized local control (low y) but has high trust in government
        authority = values.decision_authority
        gov_trust = behavior.system_trust.government
        
        auth_diff = 50.0 - authority # high when centralized
        trust_diff = gov_trust - 50.0 # high when high trust
        
        if auth_diff > 10.0 and trust_diff > 10.0:
            severity = (auth_diff * trust_diff) / 2500.0
            if severity > 0.3:
                contradictions.append(Contradiction(
                    type="decentralized_vs_gov_trust",
                    severity=round(severity, 2),
                    description="Prefers decentralized/local decision making despite high trust in centralized government",
                    related_dimensions=["decision_authority", "system_trust"]
                ))
                
        return contradictions
