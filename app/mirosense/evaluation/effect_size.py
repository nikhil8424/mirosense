"""Statistical Effect Size Analytics.

Computes Cohen's d, Hedges' g, and percent change for comparing scenario distributions.
"""

from __future__ import annotations

import math
import statistics
from typing import List, Optional, Tuple


def compute_cohens_d(group1: List[float], group2: List[float]) -> Optional[float]:
    """Compute Cohen's d effect size between two independent sample distributions.
    
    d = (mean1 - mean2) / s_pooled
    """
    n1 = len(group1)
    n2 = len(group2)
    if n1 < 2 or n2 < 2:
        return None

    m1 = statistics.mean(group1)
    m2 = statistics.mean(group2)
    v1 = statistics.variance(group1)
    v2 = statistics.variance(group2)

    # Pooled standard deviation
    s_pooled = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    if s_pooled == 0.0:
        return 0.0

    d = (m1 - m2) / s_pooled
    return round(float(d), 4)


def compute_hedges_g(group1: List[float], group2: List[float]) -> Optional[float]:
    """Compute Hedges' g (bias-corrected Cohen's d for small samples)."""
    d = compute_cohens_d(group1, group2)
    if d is None:
        return None
    n = len(group1) + len(group2)
    if n <= 3:
        return d
    correction = 1.0 - (3.0 / (4.0 * (n - 2) - 1.0))
    return round(float(d * correction), 4)
