from typing import List, Literal
from pydantic import BaseModel, Field

PrimaryDimension = Literal[
    "market_preference",
    "decision_authority",
    "fairness_preference",
    "risk_tolerance",
    "time_horizon",
    "intervention_style",
    "system_trust"
]

class Values(BaseModel):
    market_preference: float = Field(0.0, ge=0.0, le=100.0)
    decision_authority: float = Field(0.0, ge=0.0, le=100.0)
    fairness_preference: float = Field(0.0, ge=0.0, le=100.0)

class SystemTrust(BaseModel):
    government: float = Field(0.0, ge=0.0, le=100.0)
    corporate: float = Field(0.0, ge=0.0, le=100.0)
    aggregate: float = Field(0.0, ge=0.0, le=100.0)
    variance: float = Field(0.0, ge=0.0, le=100.0)

class DecisionBehavior(BaseModel):
    risk_tolerance: float = Field(0.0, ge=0.0, le=100.0)
    time_horizon: float = Field(0.0, ge=0.0, le=100.0)
    intervention_style: float = Field(0.0, ge=0.0, le=100.0)
    system_trust: SystemTrust = Field(default_factory=SystemTrust)

class CubePosition(BaseModel):
    x: float = Field(0.0, ge=0.0, le=100.0, description="Market Preference")
    y: float = Field(0.0, ge=0.0, le=100.0, description="Decision Authority")
    z: float = Field(0.0, ge=0.0, le=100.0, description="Risk Tolerance")

class Metadata(BaseModel):
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    consistency_score: float = Field(0.0, ge=0.0, le=1.0)

class Insight(BaseModel):
    type: str
    title: str
    description: str
    related_dimensions: List[PrimaryDimension]

class Contradiction(BaseModel):
    type: str
    severity: float = Field(..., ge=0.0, le=1.0)
    description: str
    related_dimensions: List[PrimaryDimension]

class Profile(BaseModel):
    values: Values = Field(default_factory=Values)
    decision_behavior: DecisionBehavior = Field(default_factory=DecisionBehavior)
    cube_position: CubePosition = Field(default_factory=CubePosition)
    metadata: Metadata = Field(default_factory=Metadata)
    insights: List[Insight] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
