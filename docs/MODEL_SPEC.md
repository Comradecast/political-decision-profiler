# Model Specification (V1.1)

## System Type

Constraint-Based Political Decision Profiler

---

## Data Model

```json
{
  "values": {
    "market_preference": 0,
    "decision_authority": 0,
    "fairness_preference": 0
  },
  "decision_behavior": {
    "risk_tolerance": 0,
    "time_horizon": 0,
    "intervention_style": 0,
    "system_trust": {
      "government": 0,
      "corporate": 0,
      "aggregate": 0,
      "variance": 0
    }
  },
  "cube_position": {
    "x": 0,
    "y": 0,
    "z": 0
  },
  "metadata": {
    "confidence_score": 0.0,
    "consistency_score": 0.0
  },
  "insights": [],
  "contradictions": []
}
```

---

## Scoring Logic

### Dimension Scoring

* Each answer contributes weighted values to one or more dimensions
* Scores normalized to 0–100

---

### Cube Projection

* X = Market Preference
* Y = Decision Authority
* Z = Risk Tolerance

---

## System Trust Calculation

* Aggregate = average of sub-scores
* Variance = difference between sub-scores

---

## Confidence Score

Measures decisiveness:

confidence_score = 1 - (neutral_answers / total_answers)

---

## Consistency Score

Measures internal coherence:

consistency_score = 1 - average(contradiction_severity)

---

## Contradiction Engine

Contradictions are not errors—they are signals.

Example:

```json
{
  "type": "market_vs_intervention",
  "severity": 0.72,
  "description": "Prefers market outcomes but supports early intervention under uncertainty"
}
```

---

## System Requirements

* Reject invalid questions automatically
* Enforce dimension separation
* Detect cross-axis contradictions
* Prevent low-signal inputs

---

## Output Philosophy

The system does not label ideology.

It describes:

* What you prefer
* How you decide
* Where those conflict
