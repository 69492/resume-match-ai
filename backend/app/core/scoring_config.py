"""Configuration for the deterministic match score engine.

The score bands are product interpretation bands, not scientifically validated
hiring thresholds.
"""

REQUIRED_WEIGHT = 0.80
PREFERRED_WEIGHT = 0.20

# Ordered from highest to lowest minimum score.
SCORE_BANDS = (
    (90.0, "Excellent Match"),
    (75.0, "Strong Match"),
    (60.0, "Moderate Match"),
    (40.0, "Weak Match"),
    (0.0, "Low Match"),
)
