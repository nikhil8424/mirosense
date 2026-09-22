"""Unit tests for scenario specifications and engine."""

from pathlib import Path
from app.mirosense.schemas.scenarios import Scenario
from app.mirosense.evaluation.scenario_engine import ScenarioEngine


def test_scenario_creation_and_persistence(tmp_path: Path):
    engine = ScenarioEngine(storage_dir=str(tmp_path / "scenarios"))

    scen = engine.create_scenario(
        name="Fare-Free Bus Transit",
        description="6-month pilot of free weekend buses",
        intervention_text="All municipal buses free on weekends.",
        policy_parameters={"fare": 0.0, "coverage": "weekends"},
        random_seed=12345,
    )

    assert scen.scenario_id.startswith("scen_")
    assert scen.name == "Fare-Free Bus Transit"

    loaded = engine.load_scenario(scen.scenario_id)
    assert loaded is not None
    assert loaded.name == scen.name
    assert loaded.policy_parameters["fare"] == 0.0


def test_validate_controlled_comparison():
    engine = ScenarioEngine()
    s1 = Scenario(scenario_id="s1", name="Baseline", description="", intervention_text="", simulation_parameters={"agent_count": 50, "platform": "parallel"})
    s2 = Scenario(scenario_id="s2", name="Policy A", description="", intervention_text="", simulation_parameters={"agent_count": 50, "platform": "parallel"})
    s3 = Scenario(scenario_id="s3", name="Policy B (Confounded)", description="", intervention_text="", simulation_parameters={"agent_count": 100, "platform": "twitter"})

    # s1 vs s2 is clean
    warnings_clean = engine.validate_controlled_comparison([s1, s2])
    assert len(warnings_clean) == 0

    # s1 vs s3 has confounding differences in agent_count and platform
    warnings_confounded = engine.validate_controlled_comparison([s1, s3])
    assert len(warnings_confounded) == 2
