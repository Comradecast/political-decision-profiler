import pytest
from src.schema.question_schema import Question, Option
from src.scoring.scorer import Scorer

def test_scorer_initialization():
    scorer = Scorer()
    assert scorer.raw_scores["market_preference"] == 0.0
    assert scorer.counts["market_preference"] == 0

def test_process_response():
    scorer = Scorer()
    q = Question(
        id="q1",
        scenario="A test",
        primary_dimension="market_preference",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Opt1", scoring_effects={"market_preference": 50.0, "risk_tolerance": 20.0}),
            Option(id="o2", label="Opt2", scoring_effects={"market_preference": -50.0})
        ]
    )
    scorer.process_response(q, "o1")
    assert scorer.raw_scores["market_preference"] == 50.0
    assert scorer.raw_scores["risk_tolerance"] == 20.0
    assert scorer.counts["market_preference"] == 1
    assert scorer.counts["risk_tolerance"] == 1

def test_process_response_invalid_option():
    scorer = Scorer()
    q = Question(
        id="q1",
        scenario="A test",
        primary_dimension="market_preference",
        tradeoff_present=True,
        uncertainty_present=False,
        options=[
            Option(id="o1", label="Opt1", scoring_effects={"market_preference": 50.0}),
            Option(id="o2", label="Opt2", scoring_effects={"market_preference": -50.0})
        ]
    )
    with pytest.raises(ValueError, match="not found in question"):
        scorer.process_response(q, "o3")

def test_normalization():
    scorer = Scorer()
    
    # +100 out of a possible +/- 100 -> top of the scale (100)
    assert scorer._normalize(100.0, 1) == 100.0
    
    # -100 out of possible +/- 100 -> bottom of scale (0)
    assert scorer._normalize(-100.0, 1) == 0.0
    
    # 0 out of possible +/- 100 -> middle of scale (50)
    assert scorer._normalize(0.0, 1) == 50.0
    
    # +50 out of possible +/- 100 -> 75% scale
    assert scorer._normalize(50.0, 1) == 75.0
    
    # Multiple questions
    # +100 +50 = 150 out of possible +/- 200 -> 350 / 400 = 87.5% scale
    assert scorer._normalize(150.0, 2) == 87.5

def test_get_system_trust():
    scorer = Scorer()
    scorer.raw_scores["system_trust_government"] = 50.0
    scorer.counts["system_trust_government"] = 1
    
    scorer.raw_scores["system_trust_corporate"] = -50.0
    scorer.counts["system_trust_corporate"] = 1
    
    st = scorer.get_system_trust()
    assert st.government == 75.0 # (50 + 100) / 200 * 100
    assert st.corporate == 25.0  # (-50 + 100) / 200 * 100
    assert st.aggregate == 50.0
    assert st.variance == 50.0

def test_get_values_and_cube():
    scorer = Scorer()
    scorer.raw_scores["market_preference"] = 100.0
    scorer.counts["market_preference"] = 1
    scorer.raw_scores["decision_authority"] = -100.0
    scorer.counts["decision_authority"] = 1
    scorer.raw_scores["risk_tolerance"] = 0.0
    scorer.counts["risk_tolerance"] = 1
    
    v = scorer.get_values()
    assert v.market_preference == 100.0
    assert v.decision_authority == 0.0
    
    cp = scorer.get_cube_position()
    assert cp.x == 100.0
    assert cp.y == 0.0
    assert cp.z == 50.0
