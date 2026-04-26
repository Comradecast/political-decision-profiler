from typing import Dict, Literal
from pydantic import BaseModel, Field, field_validator

DimensionKey = Literal[
    "market_preference",
    "decision_authority",
    "fairness_preference",
    "risk_tolerance",
    "time_horizon",
    "intervention_style",
    "system_trust_government",
    "system_trust_corporate",
]

PrimaryDimension = Literal[
    "market_preference",
    "decision_authority",
    "fairness_preference",
    "risk_tolerance",
    "time_horizon",
    "intervention_style",
    "system_trust"
]

class Option(BaseModel):
    id: str = Field(..., description="Unique identifier for the option")
    label: str = Field(..., description="The text of the option")
    scoring_effects: Dict[DimensionKey, float] = Field(
        ..., description="Map of dimension keys to score adjustments"
    )

    @field_validator("scoring_effects")
    @classmethod
    def validate_scoring_effects(cls, v: Dict[DimensionKey, float]) -> Dict[DimensionKey, float]:
        if not v:
            raise ValueError("scoring_effects cannot be empty")
        for val in v.values():
            if val < -100.0 or val > 100.0:
                raise ValueError("scoring effects must be between -100.0 and 100.0")
        return v

class Question(BaseModel):
    id: str = Field(..., description="Unique identifier for the question")
    scenario: str = Field(..., description="The scenario description")
    primary_dimension: PrimaryDimension = Field(..., description="Primary dimension being tested")
    secondary_dimension: PrimaryDimension | None = Field(
        None, description="Optional secondary dimension being tested"
    )
    options: list[Option] = Field(..., min_length=2, description="List of possible answers")
    
    tradeoff_present: bool = Field(..., description="Flag indicating if a tradeoff is present")
    uncertainty_present: bool = Field(..., description="Flag indicating if uncertainty is present")

    @field_validator("options")
    @classmethod
    def options_must_have_unique_ids(cls, v: list[Option]) -> list[Option]:
        ids = [opt.id for opt in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Option IDs must be unique within a question")
        return v
