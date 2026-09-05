"""Scenario Designer - Research layer for scenario/decision modeling.

This layer introduces an explicit scenario/decision layer for evaluating
multiple candidate decisions. Each scenario represents a decision/intervention
being evaluated in the simulation.

Foundation: Builds on existing simulation configuration infrastructure.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..utils.logger import get_logger

logger = get_logger('mirofish.research.scenario_designer')


@dataclass
class Scenario:
    """Represents a candidate decision/intervention scenario."""
    
    scenario_id: str
    name: str
    description: str
    
    # Decision/intervention details
    intervention: str
    assumptions: List[str] = field(default_factory=list)
    
    # Simulation parameters
    platform: str = "reddit"  # twitter, reddit, parallel
    max_rounds: int = 10
    agent_count: int = 50
    
    # Context
    context_id: Optional[str] = None
    problem_statement: str = ""
    
    # Simulation linkage
    simulation_id: Optional[str] = None
    simulation_config: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"  # pending, running, completed, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'scenario_id': self.scenario_id,
            'name': self.name,
            'description': self.description,
            'intervention': self.intervention,
            'assumptions': self.assumptions,
            'platform': self.platform,
            'max_rounds': self.max_rounds,
            'agent_count': self.agent_count,
            'context_id': self.context_id,
            'problem_statement': self.problem_statement,
            'simulation_id': self.simulation_id,
            'simulation_config': self.simulation_config,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'status': self.status,
        }


class ScenarioDesigner:
    """Research-oriented Scenario Designer.
    
    This component provides a structured approach to designing and managing
    decision scenarios for simulation.
    
    The designer:
    1. Defines candidate decisions/interventions
    2. Specifies scenario assumptions and parameters
    3. Links scenarios to community context
    4. Manages scenario lifecycle
    5. Supports multiple scenario execution
    """
    
    def __init__(self):
        self._scenarios: Dict[str, Scenario] = {}
        logger.info("ScenarioDesigner initialized")
    
    def create_scenario(
        self,
        name: str,
        description: str,
        intervention: str,
        assumptions: Optional[List[str]] = None,
        platform: str = "reddit",
        max_rounds: int = 10,
        agent_count: int = 50,
        context_id: Optional[str] = None,
        problem_statement: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Scenario:
        """Create a new scenario.
        
        Args:
            name: Scenario name
            description: Scenario description
            intervention: The decision/intervention being evaluated
            assumptions: List of scenario assumptions
            platform: Simulation platform
            max_rounds: Maximum simulation rounds
            agent_count: Number of agents (5-500)
            context_id: Community context identifier
            problem_statement: The problem being addressed
            metadata: Additional metadata
            
        Returns:
            Scenario object
        """
        scenario_id = f"scenario_{uuid.uuid4().hex[:12]}"
        
        scenario = Scenario(
            scenario_id=scenario_id,
            name=name,
            description=description,
            intervention=intervention,
            assumptions=assumptions or [],
            platform=platform,
            max_rounds=max_rounds,
            agent_count=agent_count,
            context_id=context_id,
            problem_statement=problem_statement,
            metadata=metadata or {},
        )
        
        self._scenarios[scenario_id] = scenario
        logger.info(f"Created scenario: {scenario_id} - {name}")
        
        return scenario
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Retrieve a scenario by ID.
        
        Args:
            scenario_id: Scenario identifier
            
        Returns:
            Scenario if found, None otherwise
        """
        return self._scenarios.get(scenario_id)
    
    def list_scenarios(
        self,
        context_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Scenario]:
        """List scenarios with optional filtering.
        
        Args:
            context_id: Filter by context ID
            status: Filter by status
            
        Returns:
            List of scenarios
        """
        scenarios = list(self._scenarios.values())
        
        if context_id:
            scenarios = [s for s in scenarios if s.context_id == context_id]
        
        if status:
            scenarios = [s for s in scenarios if s.status == status]
        
        return scenarios
    
    def update_scenario(
        self,
        scenario_id: str,
        **updates: Any,
    ) -> Optional[Scenario]:
        """Update a scenario.
        
        Args:
            scenario_id: Scenario identifier
            **updates: Fields to update
            
        Returns:
            Updated scenario if found, None otherwise
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            logger.warning(f"Scenario not found: {scenario_id}")
            return None
        
        for key, value in updates.items():
            if hasattr(scenario, key):
                setattr(scenario, key, value)
        
        logger.info(f"Updated scenario: {scenario_id}")
        return scenario
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario.
        
        Args:
            scenario_id: Scenario identifier
            
        Returns:
            True if deleted, False if not found
        """
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            logger.info(f"Deleted scenario: {scenario_id}")
            return True
        return False
    
    def link_simulation(
        self,
        scenario_id: str,
        simulation_id: str,
        simulation_config: Dict[str, Any],
    ) -> bool:
        """Link a scenario to a simulation.
        
        Args:
            scenario_id: Scenario identifier
            simulation_id: Simulation identifier
            simulation_config: Simulation configuration
            
        Returns:
            True if linked, False if scenario not found
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            logger.warning(f"Scenario not found: {scenario_id}")
            return False
        
        scenario.simulation_id = simulation_id
        scenario.simulation_config = simulation_config
        scenario.status = "running"
        
        logger.info(f"Linked scenario {scenario_id} to simulation {simulation_id}")
        return True
    
    def mark_scenario_completed(
        self,
        scenario_id: str,
        success: bool = True,
    ) -> bool:
        """Mark a scenario as completed.
        
        Args:
            scenario_id: Scenario identifier
            success: Whether simulation was successful
            
        Returns:
            True if updated, False if scenario not found
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            return False
        
        scenario.status = "completed" if success else "failed"
        logger.info(f"Marked scenario {scenario_id} as {scenario.status}")
        return True


class ScenarioManager:
    """Manages multiple scenarios for decision comparison.
    
    This component handles the lifecycle of multiple scenarios
    and provides comparison capabilities.
    """
    
    def __init__(self):
        self.designer = ScenarioDesigner()
        logger.info("ScenarioManager initialized")
    
    def create_decision_problem(
        self,
        problem_statement: str,
        context_id: Optional[str] = None,
    ) -> str:
        """Create a decision problem context.
        
        Args:
            problem_statement: The community problem
            context_id: Community context identifier
            
        Returns:
            Problem identifier (uses context_id or generates one)
        """
        import uuid as _uuid
        
        if not context_id:
            context_id = f"problem_{_uuid.uuid4().hex[:12]}"
        
        logger.info(f"Created decision problem: {context_id}")
        return context_id
    
    def add_candidate_decision(
        self,
        problem_id: str,
        name: str,
        description: str,
        intervention: str,
        assumptions: Optional[List[str]] = None,
        **scenario_params: Any,
    ) -> Scenario:
        """Add a candidate decision to a problem.
        
        Args:
            problem_id: Problem identifier
            name: Decision name
            description: Decision description
            intervention: The intervention being evaluated
            assumptions: Decision assumptions
            **scenario_params: Additional scenario parameters
            
        Returns:
            Created Scenario
        """
        scenario = self.designer.create_scenario(
            name=name,
            description=description,
            intervention=intervention,
            assumptions=assumptions,
            context_id=problem_id,
            problem_statement=problem_id,
            **scenario_params,
        )
        
        logger.info(f"Added candidate decision to problem {problem_id}: {name}")
        return scenario
    
    def get_candidate_decisions(
        self,
        problem_id: str,
    ) -> List[Scenario]:
        """Get all candidate decisions for a problem.
        
        Args:
            problem_id: Problem identifier
            
        Returns:
            List of scenarios
        """
        return self.designer.list_scenarios(context_id=problem_id)
    
    def compare_scenarios(
        self,
        problem_id: str,
    ) -> Dict[str, Any]:
        """Compare scenarios for a decision problem.
        
        Args:
            problem_id: Problem identifier
            
        Returns:
            Comparison summary
        """
        scenarios = self.get_candidate_decisions(problem_id)
        
        comparison = {
            'problem_id': problem_id,
            'scenario_count': len(scenarios),
            'scenarios': [s.to_dict() for s in scenarios],
            'completed_count': sum(1 for s in scenarios if s.status == 'completed'),
            'running_count': sum(1 for s in scenarios if s.status == 'running'),
            'pending_count': sum(1 for s in scenarios if s.status == 'pending'),
        }
        
        return comparison
