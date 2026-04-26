import pytest
from pydantic import ValidationError
from src.schema.question_schema import Option, Question

def test_option_valid():
    opt = Option(
        id="A",
        label="Test option",
        scoring_effects={"market_preference": 10.0, "risk_tolerance": -5.0}
    )
    assert opt.id == "A"
    assert opt.scoring_effects["market_preference"] == 10.0

def test_option_invalid_dimension():
    with pytest.raises(ValidationError):
        Option(
            id="A",
            label="Test option",
            scoring_effects={"invalid_dimension": 10.0}
        )

def test_option_empty_scoring_effects():
    with pytest.raises(ValidationError, match="scoring_effects cannot be empty"):
        Option(
            id="A",
            label="Test option",
            scoring_effects={}
        )

def test_option_out_of_bounds_scoring_effects():
    with pytest.raises(ValidationError, match="scoring effects must be between -100.0 and 100.0"):
        Option(
            id="A",
            label="Test option",
            scoring_effects={"market_preference": 150.0}
        )
    with pytest.raises(ValidationError, match="scoring effects must be between -100.0 and 100.0"):
        Option(
            id="B",
            label="Test option",
            scoring_effects={"market_preference": -150.0}
        )

def test_question_valid():
    q = Question(
        id="q1",
        scenario="A test scenario",
        primary_dimension="market_preference",
        options=[
            Option(id="opt1", label="Opt 1", scoring_effects={"market_preference": 5.0}),
            Option(id="opt2", label="Opt 2", scoring_effects={"market_preference": -5.0})
        ],
        tradeoff_present=True,
        uncertainty_present=False
    )
    assert q.id == "q1"
    assert q.primary_dimension == "market_preference"

def test_question_primary_dimension_system_trust():
    q = Question(
        id="q2",
        scenario="A test scenario",
        primary_dimension="system_trust",
        options=[
            Option(id="opt1", label="Opt 1", scoring_effects={"system_trust_government": 5.0}),
            Option(id="opt2", label="Opt 2", scoring_effects={"system_trust_government": -5.0})
        ],
        tradeoff_present=True,
        uncertainty_present=False
    )
    assert q.primary_dimension == "system_trust"

def test_question_invalid_primary_dimension():
    with pytest.raises(ValidationError):
        Question(
            id="q3",
            scenario="A test scenario",
            primary_dimension="system_trust_government",
            options=[
                Option(id="opt1", label="Opt 1", scoring_effects={"system_trust_government": 5.0}),
                Option(id="opt2", label="Opt 2", scoring_effects={"system_trust_government": -5.0})
            ],
            tradeoff_present=True,
            uncertainty_present=False
        )

def test_question_unique_option_ids():
    with pytest.raises(ValidationError):
        Question(
            id="q1",
            scenario="A test scenario",
            primary_dimension="market_preference",
            options=[
                Option(id="opt1", label="Opt 1", scoring_effects={"market_preference": 5.0}),
                Option(id="opt1", label="Opt 2", scoring_effects={"market_preference": -5.0})
            ],
            tradeoff_present=True,
            uncertainty_present=False
        )

def test_question_requires_at_least_two_options():
    with pytest.raises(ValidationError):
        Question(
            id="q1",
            scenario="A test scenario",
            primary_dimension="market_preference",
            options=[
                Option(id="opt1", label="Opt 1", scoring_effects={"market_preference": 5.0})
            ],
            tradeoff_present=True,
            uncertainty_present=False
        )
