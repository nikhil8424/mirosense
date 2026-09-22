"""Unit tests for scenario comparison and effect size calculation."""

from app.mirosense.evaluation.scenario_comparison import ScenarioComparator, ScenarioProfile
from app.mirosense.evaluation.effect_size import compute_cohens_d, compute_hedges_g


def test_cohens_d_effect_size():
    group_a = [0.85, 0.88, 0.82, 0.86, 0.84]
    group_b = [0.55, 0.58, 0.52, 0.56, 0.54]

    d = compute_cohens_d(group_a, group_b)
    g = compute_hedges_g(group_a, group_b)

    assert d is not None and d > 2.0  # Large positive effect
    assert g is not None and g > 2.0


def test_scenario_comparison_report():
    p_base = ScenarioProfile(
        scenario_id="s_base", scenario_name="Baseline Status Quo",
        acceptance=0.50, agreement=0.60, polarization=0.40, conflict_rate=0.20, stability=0.70
    )
    p_alt = ScenarioProfile(
        scenario_id="s_alt", scenario_name="Fare-Free Transit",
        acceptance=0.78, agreement=0.75, polarization=0.25, conflict_rate=0.10, stability=0.85
    )

    comparator = ScenarioComparator()
    report = comparator.compare([p_base, p_alt], baseline_id="s_base")

    assert len(report.scenarios) == 2
    assert "s_alt" in report.pairwise_differences
    diff = report.pairwise_differences["s_alt"]
    assert diff["acceptance"] == 0.28
    assert diff["polarization"] == -0.15
    assert diff["conflict_rate"] == -0.10
    assert len(report.summary_findings) > 0
