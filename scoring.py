"""
Scoring and Labeling for Provenance Guard.
← YOU BUILD THIS IN MILESTONES 4 & 5

Combines the model signal (Signal 1) and the stylometry signal (Signal 2),
applies disagreement dampening, and maps scores to user transparency labels.
"""

import config


def combine_signals(
    signal_1: float,
    signal_2: float,
    w1: float = 0.65,
    w2: float = 0.35,
) -> float:
    """
    Combine Signal 1 (predictability) and Signal 2 (stylometry) into a single score.
    Higher means more likely AI (0.0 to 1.0).
    ← Milestone 4

    Rule:
      1. Weighted average of Signal 1 (0.65) and Signal 2 (0.35).
      2. If signals disagree sharply (|s1 - s2| > 0.40), dampen the score
         toward 0.50 (uncertainty zone) to reflect conflicting evidence.
    """
    s1 = max(0.0, min(1.0, float(signal_1)))
    s2 = max(0.0, min(1.0, float(signal_2)))

    raw_blend = (w1 * s1) + (w2 * s2)
    disagreement = abs(s1 - s2)

    # Disagreement guardrail
    if disagreement > 0.40:
        pull = (disagreement - 0.40) * 0.5
        if raw_blend > 0.50:
            combined = raw_blend - pull
        else:
            combined = raw_blend + pull
    else:
        combined = raw_blend

    return round(min(1.0, max(0.0, combined)), 4)


def score_to_label(confidence: float) -> str:
    """
    Maps continuous confidence score to one of three transparent human-facing labels:
    - [0.00 - 0.38]: high-confidence human
    - (0.38 - 0.68): unsure
    - [0.68 - 1.00]: high-confidence AI
    """
    score = float(confidence)
    if score >= 0.68:
        return "high-confidence AI"
    elif score <= 0.38:
        return "high-confidence human"
    else:
        return "unsure"


def scoring_label_ranges() -> dict:
    """Helper describing the thresholds for the README."""
    return {
        "high-confidence human": "0.00 <= score <= 0.38",
        "unsure": "0.38 < score < 0.68",
        "high-confidence AI": "0.68 <= score <= 1.00",
    }