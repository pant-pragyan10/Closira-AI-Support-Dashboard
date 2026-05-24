def calibrate_confidence(raw: float, *, category: str = "generic", source_used: bool = False, deterministic: bool = False) -> float:
    """Calibrate raw confidence into realistic ranges by category.

    - raw: model-provided confidence in [0,1] (may be 0)
    - category: one of 'faq', 'mixed', 'unsupported', 'medical', 'gibberish', 'summary'
    - source_used: whether SOP/source was used
    - deterministic: whether deterministic extraction (SOP lookup) was used
    Returns value in 0.0-1.0
    """
    # clamp raw
    r = max(0.0, min(1.0, float(raw or 0.0)))

    # Base mapping per category
    buckets = {
        "faq": (0.85, 0.98),
        "mixed": (0.65, 0.85),
        "unsupported": (0.2, 0.5),
        "medical": (0.4, 0.7),
        "gibberish": (0.1, 0.3),
        "summary": (0.6, 0.9),
        "generic": (0.4, 0.9),
    }

    lo, hi = buckets.get(category, buckets["generic"])

    # If deterministic and source used, prefer upper half
    if deterministic and source_used:
        return round(lo + (hi - lo) * 0.9, 2)

    # Blend raw into range: treat raw as confidence multiplier
    calibrated = lo + (hi - lo) * r

    # If source_used boosts slightly
    if source_used:
        calibrated = min(1.0, calibrated + 0.05)

    return round(max(0.0, min(1.0, calibrated)), 2)
