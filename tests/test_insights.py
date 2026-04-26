from src.schema.profile_schema import (
    Contradiction,
    DecisionBehavior,
    Metadata,
    Profile,
    SystemTrust,
    Values,
)
from src.scoring.insights import generate_insights


def test_high_and_low_dimensions_produce_tendency_insights():
    profile = Profile(
        values=Values(
            market_preference=80.0,
            decision_authority=20.0,
            fairness_preference=50.0,
        ),
        decision_behavior=DecisionBehavior(
            risk_tolerance=50.0,
            time_horizon=50.0,
            intervention_style=50.0,
            system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0),
        ),
        metadata=Metadata(confidence_score=0.0, consistency_score=1.0),
    )

    insights = generate_insights(profile)

    assert [insight.title for insight in insights] == [
        "Market-Oriented",
        "Prefers Centralized Authority",
    ]
    assert all(insight.type == "dimension_tendency" for insight in insights)


def test_contradictions_produce_insight_entries():
    profile = Profile(
        values=Values(market_preference=50.0, decision_authority=50.0, fairness_preference=50.0),
        decision_behavior=DecisionBehavior(
            risk_tolerance=50.0,
            time_horizon=50.0,
            intervention_style=50.0,
            system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0),
        ),
        metadata=Metadata(confidence_score=0.0, consistency_score=1.0),
        contradictions=[
            Contradiction(
                type="relationship_conflict",
                severity=0.8,
                description="Market preference and risk tolerance usually move together",
                related_dimensions=["market_preference", "risk_tolerance"],
            )
        ]
    )

    insights = generate_insights(profile)

    assert len(insights) == 1
    assert insights[0].type == "contradiction"
    assert insights[0].title == "Conflicting Tendencies Detected"
    assert insights[0].description == "Market preference and risk tolerance usually move together"
    assert insights[0].related_dimensions == ["market_preference", "risk_tolerance"]


def test_meta_insights_trigger_correctly():
    profile = Profile(
        metadata=Metadata(confidence_score=0.95, consistency_score=0.5),
        contradictions=[
            Contradiction(
                type="relationship_conflict",
                severity=0.7,
                description="First conflict",
                related_dimensions=["market_preference", "risk_tolerance"],
            ),
            Contradiction(
                type="profile_incoherence",
                severity=0.8,
                description="Second conflict",
                related_dimensions=["decision_authority", "intervention_style"],
            ),
        ]
    )

    insights = generate_insights(profile)
    meta_titles = [insight.title for insight in insights if insight.type == "meta"]

    assert meta_titles == [
        "Internally Conflicted Profile",
        "Low Internal Consistency",
        "High Response Confidence",
    ]


def test_no_duplicate_insights_for_same_dimension():
    profile = Profile(
        values=Values(market_preference=90.0),
        decision_behavior=DecisionBehavior(
            risk_tolerance=50.0,
            time_horizon=50.0,
            intervention_style=50.0,
            system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0),
        ),
        metadata=Metadata(confidence_score=0.0, consistency_score=1.0),
    )

    insights = generate_insights(profile)
    market_insights = [
        insight for insight in insights
        if insight.related_dimensions == ["market_preference"]
    ]

    assert len(market_insights) == 1


def test_output_is_deterministic():
    profile = Profile(
        values=Values(market_preference=80.0, decision_authority=20.0),
        metadata=Metadata(confidence_score=0.95, consistency_score=1.0),
    )

    first = [insight.model_dump() for insight in generate_insights(profile)]
    second = [insight.model_dump() for insight in generate_insights(profile)]

    assert first == second
