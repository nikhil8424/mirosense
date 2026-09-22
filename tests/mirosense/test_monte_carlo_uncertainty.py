"""Unit tests for empirical uncertainty and Monte Carlo aggregation."""

from app.mirosense.validation.uncertainty import compute_confidence_interval
from app.mirosense.validation.monte_carlo import MonteCarloEngine
from app.mirosense.evaluation.scenario_comparison import ScenarioProfile


def test_empirical_confidence_interval():
    # 5 runs of acceptance: [0.80, 0.82, 0.78, 0.81, 0.79]
    samples = [0.80, 0.82, 0.78, 0.81, 0.79]
    ci = compute_confidence_interval(samples, metric_name="acceptance", confidence_level=0.95)

    assert ci.sample_size == 5
    assert round(ci.mean, 2) == 0.80
    assert ci.std > 0.0
    assert ci.lower_ci < ci.mean < ci.upper_ci
    assert ci.lower_ci > 0.75
    assert ci.upper_ci < 0.85


def test_monte_carlo_profile_aggregation():
    profiles = [
        ScenarioProfile(scenario_id="s1", scenario_name="Demo", acceptance=0.80, polarization=0.30, conflict_rate=0.10),
        ScenarioProfile(scenario_id="s1", scenario_name="Demo", acceptance=0.82, polarization=0.28, conflict_rate=0.12),
        ScenarioProfile(scenario_id="s1", scenario_name="Demo", acceptance=0.78, polarization=0.32, conflict_rate=0.09),
    ]

    engine = MonteCarloEngine()
    result = engine.aggregate_profiles("s1", "Demo", profiles, base_seed=100)

    assert result.runs_count == 3
    assert len(result.seeds_evaluated) == 3
    assert "acceptance" in result.statistical_summary
    acc_summary = result.statistical_summary["acceptance"]
    assert acc_summary["mean"] == 0.80
    assert acc_summary["lower_ci"] < 0.80 < acc_summary["upper_ci"]
