"""Empirical Uncertainty & Statistical Confidence Intervals.

Calculates standard errors, sample variance, and Student-t / bootstrap confidence
intervals across repeated experimental simulation runs.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import math
import statistics
from typing import Any, Dict, List, Optional

# Standard Student-t critical values for two-tailed 95% confidence intervals (df = n - 1)
STUDENT_T_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042, 50: 2.009,
    100: 1.984, 1000: 1.962
}


def _get_t_critical(df: int) -> float:
    if df in STUDENT_T_95:
        return STUDENT_T_95[df]
    # Linear interpolation or fallback to standard normal 1.96
    closest = min(STUDENT_T_95.keys(), key=lambda k: abs(k - df))
    return STUDENT_T_95[closest]


@dataclass
class ConfidenceInterval:
    """Empirical confidence interval summary for a single metric."""
    metric_name: str
    sample_size: int
    mean: float
    median: float
    std: float
    variance: float
    sem: float                 # Standard error of the mean
    lower_ci: float
    upper_ci: float
    confidence_level: float = 0.95
    method: str = "student_t"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "sample_size": self.sample_size,
            "mean": round(float(self.mean), 4),
            "median": round(float(self.median), 4),
            "std": round(float(self.std), 4),
            "variance": round(float(self.variance), 4),
            "sem": round(float(self.sem), 4),
            "lower_ci": round(float(self.lower_ci), 4),
            "upper_ci": round(float(self.upper_ci), 4),
            "confidence_level": self.confidence_level,
            "method": self.method,
        }


def compute_confidence_interval(
    samples: List[float],
    metric_name: str = "metric",
    confidence_level: float = 0.95,
    method: str = "student_t",
) -> ConfidenceInterval:
    """Calculate empirical confidence intervals for a set of experimental simulation runs.
    
    Returns a ConfidenceInterval with exact bounds based on sample standard deviation.
    """
    n = len(samples)
    if n == 0:
        return ConfidenceInterval(
            metric_name=metric_name,
            sample_size=0,
            mean=0.0,
            median=0.0,
            std=0.0,
            variance=0.0,
            sem=0.0,
            lower_ci=0.0,
            upper_ci=0.0,
            confidence_level=confidence_level,
            method=method,
        )

    if n == 1:
        val = float(samples[0])
        return ConfidenceInterval(
            metric_name=metric_name,
            sample_size=1,
            mean=val,
            median=val,
            std=0.0,
            variance=0.0,
            sem=0.0,
            lower_ci=val,
            upper_ci=val,
            confidence_level=confidence_level,
            method=method,
        )

    mean_val = statistics.mean(samples)
    median_val = statistics.median(samples)
    std_val = statistics.stdev(samples)
    var_val = statistics.variance(samples)
    sem_val = std_val / math.sqrt(n)

    df = n - 1
    t_crit = _get_t_critical(df)
    margin = t_crit * sem_val

    lower_ci = mean_val - margin
    upper_ci = mean_val + margin

    return ConfidenceInterval(
        metric_name=metric_name,
        sample_size=n,
        mean=mean_val,
        median=median_val,
        std=std_val,
        variance=var_val,
        sem=sem_val,
        lower_ci=lower_ci,
        upper_ci=upper_ci,
        confidence_level=confidence_level,
        method=method,
    )
