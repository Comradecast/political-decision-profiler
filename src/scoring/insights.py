from typing import List
from src.schema.profile_schema import Insight, PrimaryDimension, Profile

HIGH_THRESHOLD = 70.0
LOW_THRESHOLD = 30.0

DIMENSION_RULES = {
    "market_preference": {
        "high": (
            "Market-Oriented",
            "Your responses tend to favor market-based solutions and decentralized exchange.",
        ),
        "low": (
            "State-Oriented",
            "Your responses tend to favor public coordination and state-led solutions.",
        ),
    },
    "decision_authority": {
        "high": (
            "Prefers Decentralized Authority",
            "Your responses tend to favor local or distributed decision-making authority.",
        ),
        "low": (
            "Prefers Centralized Authority",
            "Your responses tend to favor centralized decision-making authority.",
        ),
    },
    "fairness_preference": {
        "high": (
            "Opportunity-Focused Fairness",
            "Your responses tend to emphasize equal opportunity as the basis for fairness.",
        ),
        "low": (
            "Outcome-Focused Fairness",
            "Your responses tend to emphasize outcomes as the basis for fairness.",
        ),
    },
    "risk_tolerance": {
        "high": (
            "High Risk Tolerance",
            "Your responses tend to accept uncertainty and potential downside for possible gains.",
        ),
        "low": (
            "Risk-Averse",
            "Your responses tend to prefer caution and downside protection.",
        ),
    },
    "time_horizon": {
        "high": (
            "Long-Term Focus",
            "Your responses tend to prioritize long-term outcomes over immediate effects.",
        ),
        "low": (
            "Short-Term Focus",
            "Your responses tend to prioritize immediate effects over long-term outcomes.",
        ),
    },
    "intervention_style": {
        "high": (
            "Reactive / Hands-Off",
            "Your responses tend to favor waiting or limiting intervention until problems are clearer.",
        ),
        "low": (
            "Proactive / Preventative",
            "Your responses tend to favor early intervention to prevent potential problems.",
        ),
    },
    "system_trust": {
        "high": (
            "High System Trust",
            "Your responses tend to express confidence in major institutions and systems.",
        ),
        "low": (
            "Low System Trust",
            "Your responses tend to express skepticism toward major institutions and systems.",
        ),
    },
}


def _dimension_scores(profile: Profile) -> list[tuple[PrimaryDimension, float]]:
    return [
        ("market_preference", profile.values.market_preference),
        ("decision_authority", profile.values.decision_authority),
        ("fairness_preference", profile.values.fairness_preference),
        ("risk_tolerance", profile.decision_behavior.risk_tolerance),
        ("time_horizon", profile.decision_behavior.time_horizon),
        ("intervention_style", profile.decision_behavior.intervention_style),
        ("system_trust", profile.decision_behavior.system_trust.aggregate),
    ]


def _tendency_for_score(score: float) -> str | None:
    if score >= HIGH_THRESHOLD:
        return "high"
    if score <= LOW_THRESHOLD:
        return "low"
    return None


def generate_insights(profile: Profile) -> List[Insight]:
    insights: List[Insight] = []
    dimensions_seen = set()

    for dimension, score in _dimension_scores(profile):
        tendency = _tendency_for_score(score)
        if tendency is None or dimension in dimensions_seen:
            continue

        title, description = DIMENSION_RULES[dimension][tendency]
        insights.append(Insight(
            type="dimension_tendency",
            title=title,
            description=description,
            related_dimensions=[dimension],
        ))
        dimensions_seen.add(dimension)

    for contradiction in profile.contradictions:
        insights.append(Insight(
            type="contradiction",
            title="Conflicting Tendencies Detected",
            description=contradiction.description,
            related_dimensions=contradiction.related_dimensions,
        ))

    if len(profile.contradictions) >= 2:
        insights.append(Insight(
            type="meta",
            title="Internally Conflicted Profile",
            description="Your preferences show multiple competing tendencies across dimensions.",
            related_dimensions=[],
        ))

    if profile.metadata.consistency_score < 0.6:
        insights.append(Insight(
            type="meta",
            title="Low Internal Consistency",
            description="Your responses reflect significant internal tension between priorities.",
            related_dimensions=[],
        ))

    if profile.metadata.confidence_score > 0.9:
        insights.append(Insight(
            type="meta",
            title="High Response Confidence",
            description="Your responses consistently expressed strong directional preferences.",
            related_dimensions=[],
        ))

    return insights
