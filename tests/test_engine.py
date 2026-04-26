import pytest
from src.schema.question_schema import Question, Option
from src.core.engine import ProfilerEngine

def test_engine_process_responses():
    engine = ProfilerEngine()
    
    q1 = Question(
        id="q1",
        scenario="A tradeoff scenario.",
        primary_dimension="market_preference",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Option 1", scoring_effects={"market_preference": 100.0}),
            Option(id="o2", label="Option 2", scoring_effects={"market_preference": -100.0})
        ]
    )
    
    q2 = Question(
        id="q2",
        scenario="A possible intervention scenario.",
        primary_dimension="intervention_style",
        tradeoff_present=True,
        uncertainty_present=True,
        options=[
            Option(id="o1", label="Option 1", scoring_effects={"intervention_style": 100.0}),
            Option(id="o2", label="Option 2", scoring_effects={"intervention_style": -100.0})
        ]
    )
    
    responses = [
        (q1, "o1"), # Strong market preference (+100)
        (q2, "o2")  # Strong intervention support (-100)
    ]
    
    profile = engine.process_responses(responses)
    
    # Check values
    assert profile.values.market_preference == 100.0
    assert profile.decision_behavior.intervention_style == 0.0
    
    # Check metadata (0 neutral answers)
    assert profile.metadata.confidence_score == 1.0
    
    # We should have triggered the market_vs_intervention contradiction
    assert len(profile.contradictions) == 1
    assert profile.contradictions[0].type == "market_vs_intervention"
    assert profile.contradictions[0].severity == 1.0
    
    # Check consistency drop
    assert profile.metadata.consistency_score == 0.0

def test_engine_neutral_answers():
    engine = ProfilerEngine()
    
    q1 = Question(
        id="q1",
        scenario="A tradeoff scenario.",
        primary_dimension="market_preference",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Option 1", scoring_effects={"market_preference": 0.0}),
            Option(id="o2", label="Option 2", scoring_effects={"market_preference": 10.0})
        ]
    )
    
    # Both options have identical scoring effect (violates "no signal" validator rule)
    # We will bypass the explicit "no signal" validator check for testing neutral 
    # tracking by having distinct effects, but one is all 0s.
    
    responses = [
        (q1, "o1") # Neutral
    ]
    
    profile = engine.process_responses(responses)
    
    # 1 neutral answer out of 1 -> confidence 0.0
    assert profile.metadata.confidence_score == 0.0
