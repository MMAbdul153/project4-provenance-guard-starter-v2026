"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────


def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies.
    
    Uses Coefficient of Variation (std_dev / mean) of sentence token lengths.
    Human prose tends to have high spread (CV ~ 0.6 - 1.2+).
    AI prose tends to march in step with even lengths (CV ~ 0.1 - 0.4).
    
    Returns:
        Float between 0 and 1. Higher means MORE AI-like (lower spread).
    """
    s_list = sentences(text)
    if len(s_list) < 2:
        # Edge case: 1 sentence has no spread. Return neutral uncertainty (0.50).
        return 0.50

    lengths = [len(words(s)) for s in s_list if words(s)]
    if len(lengths) < 2:
        return 0.50

    mean_len = statistics.mean(lengths)
    if mean_len == 0:
        return 0.50

    stdev_len = statistics.stdev(lengths)
    cv = stdev_len / mean_len

    # Map CV to 0-1 (higher = more AI-like / low variation)
    # A CV of 0.8+ gives ~0.3 (human); a CV of 0.2 gives ~0.7 (AI)
    ai_like_score = 1.0 / (1.0 + (cv * 1.5))
    return round(min(1.0, max(0.0, ai_like_score)), 4)


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words (lexical diversity).
    
    AI generation tends to reuse a consistent, predictable vocabulary core.
    
    Returns:
        Float between 0 and 1. Higher means MORE AI-like (lower diversity).
    """
    w_list = words(text)
    if not w_list:
        return 0.50

    unique_tokens = set(w_list)
    raw_ttr = len(unique_tokens) / len(w_list)

    # Invert so higher = more AI-like
    ai_like_ttr = 1.0 - raw_ttr
    return round(min(1.0, max(0.0, ai_like_ttr)), 4)


def punctuation_density(text: str) -> float:
    """
    How much expressive punctuation (semicolons, dashes, colons, quotes) relative to words.
    
    Humans use expressive pauses and varied punctuation. AI models tend to favor
    plain periods and standard commas.
    
    Returns:
        Float between 0 and 1. Higher means MORE AI-like (less expressive punctuation).
    """
    w_list = words(text)
    if not w_list:
        return 0.50

    # Look for expressive structural punctuation
    expressive_puncs = re.findall(r"[;:—\-\(\)\"]", text)
    rate = len(expressive_puncs) / len(w_list)

    # A rate of ~0.08+ is human; ~0.00-0.02 is typical plain AI output
    ai_like_punc = 1.0 - min(1.0, rate * 12.0)
    return round(min(1.0, max(0.0, ai_like_punc)), 4)


# ── Combining them ───────────────────────────────────────────────────────────


def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. Higher means more likely AI.
    
    Weights:
      - 50% Sentence length spread (burstiness)
      - 35% Type-token ratio (lexical repetition)
      - 15% Expressive punctuation density
    """
    spread = sentence_length_spread(text)
    ttr = type_token_ratio(text)
    punc = punctuation_density(text)

    composite = (0.50 * spread) + (0.35 * ttr) + (0.15 * punc)
    return round(min(1.0, max(0.0, composite)), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")