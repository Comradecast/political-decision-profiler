import pytest
from src.schema.question_schema import Question, Option
from src.validation.question_validator import QuestionValidator

def create_valid_base_question() -> Question:
    return Question(
        id="q1",
        scenario="A scenario with immediate cost.",
        primary_dimension="market_preference",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Option 1", scoring_effects={"market_preference": 10.0}),
            Option(id="o2", label="Option 2", scoring_effects={"market_preference": -10.0})
        ]
    )

def test_tradeoff_missing():
    q = create_valid_base_question()
    q.tradeoff_present = False
    with pytest.raises(ValueError, match="tradeoff_present must be True"):
        QuestionValidator.validate(q)

def test_no_signal_identical_effects():
    q = create_valid_base_question()
    q.options[1].scoring_effects = q.options[0].scoring_effects
    with pytest.raises(ValueError, match="No signal"):
        QuestionValidator.validate(q)

def test_risk_tolerance_with_uncertainty():
    q = create_valid_base_question()
    q.primary_dimension = "risk_tolerance"
    q.uncertainty_present = True
    q.options[0].scoring_effects = {"risk_tolerance": 10.0}
    q.options[1].scoring_effects = {"risk_tolerance": -10.0}
    with pytest.raises(ValueError, match="uncertainty_present=False"):
        QuestionValidator.validate(q)

def test_intervention_style_valid():
    q = create_valid_base_question()
    q.primary_dimension = "intervention_style"
    q.uncertainty_present = True
    q.scenario = "A possible situation."
    q.options[0].scoring_effects = {"intervention_style": 10.0}
    q.options[1].scoring_effects = {"intervention_style": -10.0}
    assert QuestionValidator.validate(q) is True

def test_intervention_style_without_uncertainty():
    q = create_valid_base_question()
    q.primary_dimension = "intervention_style"
    q.uncertainty_present = False
    q.options[0].scoring_effects = {"intervention_style": 10.0}
    q.options[1].scoring_effects = {"intervention_style": -10.0}
    with pytest.raises(ValueError, match="uncertainty_present=True"):
        QuestionValidator.validate(q)

def test_intervention_style_without_keywords():
    q = create_valid_base_question()
    q.primary_dimension = "intervention_style"
    q.uncertainty_present = True
    q.scenario = "A definite situation."
    q.options[0].scoring_effects = {"intervention_style": 10.0}
    q.options[1].scoring_effects = {"intervention_style": -10.0}
    with pytest.raises(ValueError, match="lacks uncertainty keywords"):
        QuestionValidator.validate(q)

def test_time_horizon_valid():
    q = create_valid_base_question()
    q.primary_dimension = "time_horizon"
    q.scenario = "You face an immediate cost for a later benefit."
    q.options[0].scoring_effects = {"time_horizon": 10.0}
    q.options[1].scoring_effects = {"time_horizon": -10.0}
    assert QuestionValidator.validate(q) is True

def test_time_horizon_invalid_framing():
    q = create_valid_base_question()
    q.primary_dimension = "time_horizon"
    q.scenario = "An abstract choice."
    q.options[0].scoring_effects = {"time_horizon": 10.0}
    q.options[1].scoring_effects = {"time_horizon": -10.0}
    with pytest.raises(ValueError, match="imply present cost vs delayed benefit"):
        QuestionValidator.validate(q)

def test_system_trust_valid():
    q = Question(
        id="q2",
        scenario="Do you believe the system works?",
        primary_dimension="system_trust",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Yes", scoring_effects={"system_trust_government": 10.0}),
            Option(id="o2", label="No", scoring_effects={"system_trust_government": -10.0})
        ]
    )
    assert QuestionValidator.validate(q) is True

def test_system_trust_missing_believe():
    q = Question(
        id="q2",
        scenario="The system works.",
        primary_dimension="system_trust",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Yes", scoring_effects={"system_trust_government": 10.0}),
            Option(id="o2", label="No", scoring_effects={"system_trust_government": -10.0})
        ]
    )
    with pytest.raises(ValueError, match="belief framing"):
        QuestionValidator.validate(q)

def test_system_trust_wrong_scoring_key():
    q = Question(
        id="q2",
        scenario="Do you believe the system works?",
        primary_dimension="system_trust",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Yes", scoring_effects={"system_trust_government": 10.0, "market_preference": 10.0}),
            Option(id="o2", label="No", scoring_effects={"system_trust_government": -10.0})
        ]
    )
    with pytest.raises(ValueError, match="cannot score other dimensions"):
        QuestionValidator.validate(q)

def test_isolation_more_than_two_dimensions():
    q = create_valid_base_question()
    q.options[0].scoring_effects = {
        "market_preference": 10.0,
        "risk_tolerance": 5.0,
        "decision_authority": 2.0
    }
    with pytest.raises(ValueError, match="more than 2 scoring dimensions"):
        QuestionValidator.validate(q)

def test_isolation_missing_primary():
    q = create_valid_base_question()
    q.options[0].scoring_effects = {"risk_tolerance": 10.0}
    with pytest.raises(ValueError, match="missing primary dimension"):
        QuestionValidator.validate(q)
