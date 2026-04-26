from src.schema.profile_schema import Values, DecisionBehavior, SystemTrust
from src.scoring.contradictions import ContradictionEngine


def _neutral_behavior() -> DecisionBehavior:
    return DecisionBehavior(
        risk_tolerance=50.0,
        time_horizon=50.0,
        intervention_style=50.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )


def _relationship_conflicts(values: Values, behavior: DecisionBehavior):
    return [
        contradiction for contradiction in ContradictionEngine.detect(values, behavior)
        if contradiction.type == "relationship_conflict"
    ]


def test_no_contradiction_when_balanced():
    v = Values(market_preference=50.0, decision_authority=50.0, fairness_preference=50.0)
    db = _neutral_behavior()

    contradictions = ContradictionEngine.detect(v, db)

    assert len(contradictions) == 0


def test_independent_pairs_do_not_create_pairwise_contradictions():
    v = Values(market_preference=100.0, decision_authority=50.0, fairness_preference=50.0)
    db = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=0.0, intervention_style=50.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )

    contradictions = _relationship_conflicts(v, db)

    assert contradictions == []


def test_same_direction_pairs_conflict_when_signs_oppose():
    v = Values(market_preference=100.0, decision_authority=50.0, fairness_preference=50.0)
    db = DecisionBehavior(
        risk_tolerance=0.0, time_horizon=50.0, intervention_style=50.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )

    contradictions = _relationship_conflicts(v, db)

    assert len(contradictions) == 1
    assert contradictions[0].type == "relationship_conflict"
    assert contradictions[0].severity == 0.8
    assert contradictions[0].related_dimensions == ["market_preference", "risk_tolerance"]


def test_opposite_direction_pairs_conflict_when_signs_match():
    v = Values(market_preference=100.0, decision_authority=50.0, fairness_preference=50.0)
    db = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=50.0, intervention_style=100.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )

    contradictions = _relationship_conflicts(v, db)

    assert len(contradictions) == 1
    assert contradictions[0].type == "relationship_conflict"
    assert contradictions[0].severity == 1.0
    assert contradictions[0].related_dimensions == ["market_preference", "intervention_style"]


def test_unspecified_pairs_default_to_independent():
    v = Values(market_preference=50.0, decision_authority=50.0, fairness_preference=100.0)
    db = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=0.0, intervention_style=50.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )

    contradictions = _relationship_conflicts(v, db)

    assert contradictions == []


def test_global_incoherence_detected_when_profile_is_highly_spread():
    v = Values(market_preference=100.0, decision_authority=0.0, fairness_preference=100.0)
    db = DecisionBehavior(
        risk_tolerance=0.0, time_horizon=100.0, intervention_style=0.0,
        system_trust=SystemTrust(government=100.0, corporate=100.0, aggregate=100.0, variance=0.0)
    )

    contradictions = ContradictionEngine.detect(v, db)

    assert any(c.type == "profile_incoherence" for c in contradictions)


def test_global_incoherence_uses_scaled_severity_and_top_dimensions():
    v = Values(market_preference=100.0, decision_authority=0.0, fairness_preference=100.0)
    db = DecisionBehavior(
        risk_tolerance=0.0, time_horizon=100.0, intervention_style=0.0,
        system_trust=SystemTrust(government=100.0, corporate=100.0, aggregate=100.0, variance=0.0)
    )

    incoherence = [
        c for c in ContradictionEngine.detect(v, db)
        if c.type == "profile_incoherence"
    ][0]

    assert incoherence.severity == 1.0
    assert incoherence.related_dimensions == [
        "decision_authority",
        "risk_tolerance",
        "intervention_style",
    ]


def test_relationship_conflict_severity_respects_weight():
    v = Values(market_preference=100.0, decision_authority=50.0, fairness_preference=50.0)
    db = DecisionBehavior(
        risk_tolerance=0.0, time_horizon=50.0, intervention_style=50.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )

    contradiction = _relationship_conflicts(v, db)[0]

    assert contradiction.severity == 0.8


def test_relationship_conflict_severity_is_monotonic():
    medium_values = Values(market_preference=90.0, decision_authority=50.0, fairness_preference=50.0)
    strong_values = Values(market_preference=100.0, decision_authority=50.0, fairness_preference=50.0)
    medium_behavior = DecisionBehavior(
        risk_tolerance=10.0, time_horizon=50.0, intervention_style=50.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )
    strong_behavior = DecisionBehavior(
        risk_tolerance=0.0, time_horizon=50.0, intervention_style=50.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )

    medium = _relationship_conflicts(medium_values, medium_behavior)[0]
    strong = _relationship_conflicts(strong_values, strong_behavior)[0]

    assert medium.type == "relationship_conflict"
    assert strong.type == "relationship_conflict"
    assert medium.severity < strong.severity
