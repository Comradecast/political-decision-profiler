from src.schema.profile_schema import Values, DecisionBehavior, SystemTrust
from src.scoring.contradictions import ContradictionEngine


def test_no_contradiction_when_balanced():
    v = Values(market_preference=50.0, decision_authority=50.0, fairness_preference=50.0)
    db = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=50.0, intervention_style=50.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )

    contradictions = ContradictionEngine.detect(v, db)

    assert len(contradictions) == 0


def test_contradiction_detected_when_dimensions_strongly_oppose():
    v = Values(market_preference=100.0, decision_authority=50.0, fairness_preference=50.0)
    db = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=50.0, intervention_style=0.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )

    contradictions = ContradictionEngine.detect(v, db)

    assert len(contradictions) >= 1
    assert contradictions[0].type == "vector_opposition"
    assert contradictions[0].severity == 1.0
    assert contradictions[0].related_dimensions == ["market_preference", "intervention_style"]


def test_global_incoherence_detected_when_profile_is_highly_spread():
    v = Values(market_preference=100.0, decision_authority=0.0, fairness_preference=100.0)
    db = DecisionBehavior(
        risk_tolerance=0.0, time_horizon=100.0, intervention_style=0.0,
        system_trust=SystemTrust(government=100.0, corporate=100.0, aggregate=100.0, variance=0.0)
    )

    contradictions = ContradictionEngine.detect(v, db)

    assert any(c.type == "profile_incoherence" for c in contradictions)


def test_vector_opposition_severity_is_monotonic():
    medium_values = Values(market_preference=85.0, decision_authority=50.0, fairness_preference=50.0)
    strong_values = Values(market_preference=100.0, decision_authority=50.0, fairness_preference=50.0)
    medium_behavior = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=50.0, intervention_style=15.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )
    strong_behavior = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=50.0, intervention_style=0.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )

    medium = ContradictionEngine.detect(medium_values, medium_behavior)[0]
    strong = ContradictionEngine.detect(strong_values, strong_behavior)[0]

    assert medium.type == "vector_opposition"
    assert strong.type == "vector_opposition"
    assert medium.severity < strong.severity
