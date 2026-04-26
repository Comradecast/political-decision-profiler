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
    
    # We should have triggered a contradiction
    assert len(profile.contradictions) == 1
    assert profile.contradictions[0].type == "vector_opposition"
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

def test_engine_process_responses_resets_state_between_calls():
    engine = ProfilerEngine()

    market_question = Question(
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
    risk_question = Question(
        id="q2",
        scenario="A tradeoff scenario.",
        primary_dimension="risk_tolerance",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Option 1", scoring_effects={"risk_tolerance": -100.0}),
            Option(id="o2", label="Option 2", scoring_effects={"risk_tolerance": 100.0})
        ]
    )

    first_profile = engine.process_responses([(market_question, "o1")])
    second_profile = engine.process_responses([(risk_question, "o1")])

    assert first_profile.values.market_preference == 100.0
    assert second_profile.values.market_preference == 50.0
    assert second_profile.decision_behavior.risk_tolerance == 0.0
    assert second_profile.metadata.confidence_score == 1.0

def test_engine_rejects_duplicate_question_ids():
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
        id="q1",
        scenario="Another tradeoff scenario.",
        primary_dimension="decision_authority",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Option 1", scoring_effects={"decision_authority": 100.0}),
            Option(id="o2", label="Option 2", scoring_effects={"decision_authority": -100.0})
        ]
    )

    with pytest.raises(ValueError, match="Duplicate question id in responses: q1"):
        engine.process_responses([(q1, "o1"), (q2, "o1")])

def test_engine_neutral_answers_use_small_tolerance():
    engine = ProfilerEngine()

    q1 = Question(
        id="q1",
        scenario="A tradeoff scenario.",
        primary_dimension="market_preference",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Option 1", scoring_effects={"market_preference": 0.0000005}),
            Option(id="o2", label="Option 2", scoring_effects={"market_preference": 10.0})
        ]
    )

    profile = engine.process_responses([(q1, "o1")])

    assert profile.metadata.confidence_score == 0.0
