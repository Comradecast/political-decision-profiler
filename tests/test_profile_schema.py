import pytest
from pydantic import ValidationError
from src.schema.profile_schema import (
    Values, DecisionBehavior, SystemTrust, CubePosition, Metadata,
    Insight, Contradiction, Profile
)

def test_values_valid():
    v = Values(market_preference=50.0, decision_authority=20.0, fairness_preference=100.0)
    assert v.market_preference == 50.0

def test_values_invalid_range():
    with pytest.raises(ValidationError):
        Values(market_preference=150.0)
    with pytest.raises(ValidationError):
        Values(market_preference=-10.0)

def test_system_trust_valid():
    st = SystemTrust(government=40.0, corporate=60.0, aggregate=50.0, variance=20.0)
    assert st.aggregate == 50.0

def test_decision_behavior_valid():
    db = DecisionBehavior(
        risk_tolerance=10.0, time_horizon=90.0, intervention_style=50.0,
        system_trust=SystemTrust(government=10.0, corporate=20.0, aggregate=15.0, variance=10.0)
    )
    assert db.risk_tolerance == 10.0
    assert db.system_trust.aggregate == 15.0

def test_cube_position_valid():
    cp = CubePosition(x=10.5, y=20.0, z=30.0)
    assert cp.x == 10.5

def test_cube_position_invalid_range():
    with pytest.raises(ValidationError):
        CubePosition(x=-10.0, y=20.0, z=30.0)
    with pytest.raises(ValidationError):
        CubePosition(x=10.0, y=120.0, z=30.0)

def test_metadata_valid():
    m = Metadata(confidence_score=0.8, consistency_score=0.9)
    assert m.confidence_score == 0.8

def test_metadata_invalid_range():
    with pytest.raises(ValidationError):
        Metadata(confidence_score=1.5, consistency_score=0.9)

def test_profile_valid():
    p = Profile(
        values=Values(market_preference=50.0),
        contradictions=[
            Contradiction(
                type="test", severity=0.5, description="A test contradiction",
                related_dimensions=["market_preference", "risk_tolerance"]
            )
        ],
        insights=[
            Insight(
                type="test", title="A test insight", description="A test insight",
                related_dimensions=["system_trust"]
            )
        ]
    )
    assert p.values.market_preference == 50.0
    assert len(p.contradictions) == 1
    assert p.contradictions[0].severity == 0.5
    assert p.insights[0].related_dimensions[0] == "system_trust"

def test_contradiction_invalid_severity():
    with pytest.raises(ValidationError):
        Contradiction(
            type="test", severity=1.5, description="A test", related_dimensions=["market_preference"]
        )

def test_contradiction_invalid_dimension():
    with pytest.raises(ValidationError):
        Contradiction(
            type="test", severity=0.5, description="A test", related_dimensions=["invalid_dimension"]
        )
