import pytest
from src.schema.profile_schema import Values, DecisionBehavior, SystemTrust
from src.scoring.contradictions import ContradictionEngine

def test_no_contradiction():
    v = Values(market_preference=50.0, decision_authority=50.0, fairness_preference=50.0)
    db = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=50.0, intervention_style=50.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )
    
    contradictions = ContradictionEngine.detect(v, db)
    assert len(contradictions) == 0

def test_market_vs_intervention():
    # Prefers market (high x) but supports early intervention (low intervention_style)
    v = Values(market_preference=100.0, decision_authority=50.0, fairness_preference=50.0)
    db = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=50.0, intervention_style=0.0,
        system_trust=SystemTrust(government=50.0, corporate=50.0, aggregate=50.0, variance=0.0)
    )
    
    contradictions = ContradictionEngine.detect(v, db)
    assert len(contradictions) == 1
    assert contradictions[0].type == "market_vs_intervention"
    assert contradictions[0].severity == 1.0

def test_decentralized_vs_gov_trust():
    # Prefers decentralized (low y) but has high trust in government
    v = Values(market_preference=50.0, decision_authority=0.0, fairness_preference=50.0)
    db = DecisionBehavior(
        risk_tolerance=50.0, time_horizon=50.0, intervention_style=50.0,
        system_trust=SystemTrust(government=100.0, corporate=50.0, aggregate=75.0, variance=50.0)
    )
    
    contradictions = ContradictionEngine.detect(v, db)
    assert len(contradictions) == 1
    assert contradictions[0].type == "decentralized_vs_gov_trust"
    assert contradictions[0].severity == 1.0
