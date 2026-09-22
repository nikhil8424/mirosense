"""Tests for Sensitivity, Ablation, and Baseline validation engines."""

import pytest
from app.mirosense.schemas.events import SimulationEvent, ActionType
from app.mirosense.evaluation.scenario_comparison import ScenarioProfile
from app.mirosense.validation.sensitivity import SensitivityEngine
from app.mirosense.validation.ablation import AblationEngine, AblationConfig
from app.mirosense.validation.baselines import BaselineEngine


def test_sensitivity_engine():
    profile_low = ScenarioProfile(
        scenario_id="sweep_1",
        scenario_name="Agent Count 5",
        acceptance=0.4,
        polarization=0.3,
        conflict_rate=0.2,
        modularity=0.1,
        stability=0.9,
    )
    profile_mid = ScenarioProfile(
        scenario_id="sweep_2",
        scenario_name="Agent Count 15",
        acceptance=0.6,
        polarization=0.5,
        conflict_rate=0.3,
        modularity=0.25,
        stability=0.8,
    )
    profile_high = ScenarioProfile(
        scenario_id="sweep_3",
        scenario_name="Agent Count 30",
        acceptance=0.75,
        polarization=0.7,
        conflict_rate=0.45,
        modularity=0.4,
        stability=0.7,
    )

    engine = SensitivityEngine()
    result = engine.analyze_sweep(
        parameter_name="agent_count",
        value_to_profile={5: profile_low, 15: profile_mid, 30: profile_high},
    )

    assert result.parameter_name == "agent_count"
    assert len(result.points) == 3
    assert result.points[0].acceptance == 0.4
    assert result.points[2].acceptance == 0.75
    assert result.sensitivity_indices["acceptance_range"] == pytest.approx(0.35, rel=1e-3)
    assert result.sensitivity_indices["polarization_range"] == pytest.approx(0.40, rel=1e-3)


def test_ablation_engine():
    full_profile = ScenarioProfile(
        scenario_id="full",
        scenario_name="Full Architecture",
        acceptance=0.65,
        polarization=0.4,
        conflict_rate=0.2,
        modularity=0.35,
        stability=0.85,
    )
    no_graph_profile = ScenarioProfile(
        scenario_id="no_graph",
        scenario_name="No Knowledge Graph",
        acceptance=0.50,
        polarization=0.2,
        conflict_rate=0.1,
        modularity=0.1,
        stability=0.6,
    )

    engine = AblationEngine()
    configs = engine.get_standard_ablation_configs()
    assert "FULL" in configs
    assert "NO_GRAPH" in configs
    assert configs["NO_GRAPH"].graph_grounding is False

    result = engine.evaluate_ablations(
        config_to_profile={"FULL": full_profile, "NO_GRAPH": no_graph_profile},
        baseline_name="FULL",
    )

    assert result.baseline_config == "FULL"
    assert "NO_GRAPH" in result.component_impacts
    assert result.component_impacts["NO_GRAPH"]["acceptance"] == pytest.approx(-0.15, rel=1e-3)


def test_baseline_engine():
    profile_mirosense = ScenarioProfile(
        scenario_id="scenario_1",
        scenario_name="Transit Policy A",
        acceptance=0.68,
        agreement=0.62,
        polarization=0.45,
        conflict_rate=0.22,
        modularity=0.38,
        diffusion_rate=0.55,
    )
    profile_random = ScenarioProfile(
        scenario_id="scenario_1",
        scenario_name="Random Interaction Baseline",
        acceptance=0.50,
        agreement=0.50,
        polarization=0.10,
        conflict_rate=0.50,
        modularity=0.02,
        diffusion_rate=0.20,
    )

    engine = BaselineEngine()
    result = engine.compare_baselines(
        scenario_id="scenario_1",
        scenario_name="Transit Policy A",
        profiles_by_system={"MiroSense": profile_mirosense, "Random_Baseline": profile_random},
    )

    assert result.scenario_id == "scenario_1"
    assert "MiroSense" in result.baseline_profiles
    assert "Random_Baseline" in result.baseline_profiles
    assert len(result.comparative_advantages) > 0
