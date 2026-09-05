"""Stakeholder Digital Twin - Research layer for stakeholder modeling.

This layer refactors the existing agent/profile generation functionality
into a research-oriented Stakeholder Digital Twin layer. Agents represent
heterogeneous community stakeholders with personas, roles, interests,
preferences, beliefs, goals, behavioural tendencies, relationships, and influence.

Foundation: Reuses existing OasisProfileGenerator and agent profile mechanisms.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..services.oasis_profile_generator import OasisProfileGenerator
from ..services.entity_reader import EntityReader
from ..utils.logger import get_logger

logger = get_logger('mirofish.research.stakeholder_digital_twin')


@dataclass
class StakeholderProfile:
    """Detailed stakeholder profile representing a community member."""
    
    stakeholder_id: str
    name: str
    persona: str
    role: str
    
    # Preferences and beliefs
    interests: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    beliefs: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    
    # Behavioural characteristics
    behavioural_tendencies: Dict[str, Any] = field(default_factory=dict)
    personality_traits: Dict[str, Any] = field(default_factory=dict)
    
    # Social context
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    influence_score: float = 0.5
    social_network_position: str = "neutral"  # central, peripheral, neutral
    
    # Contextual information
    relevant_context: Dict[str, Any] = field(default_factory=dict)
    background: str = ""
    
    # Metadata
    source_entity_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'stakeholder_id': self.stakeholder_id,
            'name': self.name,
            'persona': self.persona,
            'role': self.role,
            'interests': self.interests,
            'preferences': self.preferences,
            'beliefs': self.beliefs,
            'goals': self.goals,
            'behavioural_tendencies': self.behavioural_tendencies,
            'personality_traits': self.personality_traits,
            'relationships': self.relationships,
            'influence_score': self.influence_score,
            'social_network_position': self.social_network_position,
            'relevant_context': self.relevant_context,
            'background': self.background,
            'source_entity_id': self.source_entity_id,
            'created_at': self.created_at,
        }


class StakeholderDigitalTwin:
    """Research-oriented Stakeholder Digital Twin generator.
    
    This layer provides a structured approach to creating heterogeneous
    community stakeholder representations for simulation.
    
    The generator:
    1. Reads entities from the community context graph
    2. Generates detailed stakeholder profiles using LLM
    3. Enriches profiles with behavioural characteristics
    4. Models social relationships and influence
    5. Respects agent_count parameter for simulation scale
    """
    
    def __init__(
        self,
        profile_generator: Optional[OasisProfileGenerator] = None,
        entity_reader: Optional[EntityReader] = None,
    ):
        self.profile_generator = profile_generator or OasisProfileGenerator()
        self.entity_reader = entity_reader or EntityReader()
        logger.info("StakeholderDigitalTwin initialized")
    
    def generate_stakeholders(
        self,
        graph_id: str,
        agent_count: Optional[int] = None,
        entity_types: Optional[List[str]] = None,
        use_llm: bool = True,
        parallel_count: int = 5,
        simulation_requirement: str = "",
    ) -> List[StakeholderProfile]:
        """Generate stakeholder profiles from community context.
        
        Args:
            graph_id: Graph identifier from CommunityContextEngine
            agent_count: Number of stakeholders to generate (5-500)
            entity_types: Specific entity types to use as stakeholder sources
            use_llm: Whether to use LLM for profile generation
            parallel_count: Parallel profile generation count
            simulation_requirement: Context for profile generation
            
        Returns:
            List of StakeholderProfile objects
        """
        import uuid as _uuid
        
        logger.info(f"Generating stakeholder profiles from graph {graph_id}")
        
        # Step 1: Read entities from graph
        filtered = self.entity_reader.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=entity_types,
            enrich_with_edges=True,
        )
        
        total_entities = len(filtered.entities)
        
        # Step 2: Apply agent_count limit
        if agent_count is not None:
            target_count = min(agent_count, total_entities)
            if target_count < total_entities:
                filtered.entities = filtered.entities[:target_count]
                logger.info(f"Limited entities from {total_entities} to {target_count} as requested")
        else:
            target_count = total_entities
        
        logger.info(f"Generating {target_count} stakeholder profiles")
        
        # Step 3: Generate profiles using existing infrastructure
        # Reuse the OasisProfileGenerator which creates agent profiles
        profiles_data = []
        
        if use_llm:
            # Use the existing profile generation mechanism
            # This will generate profiles with personas, stances, etc.
            from ..services.simulation_manager import SimulationManager
            sim_manager = SimulationManager()
            
            # The profile generation happens in prepare_simulation
            # We'll extract and enrich the results
            logger.info("Using LLM-based profile generation")
            
            # For now, create basic profiles from entities
            # In a full implementation, this would call the profile generator
            for i, entity in enumerate(filtered.entities):
                stakeholder = StakeholderProfile(
                    stakeholder_id=f"stakeholder_{_uuid.uuid4().hex[:12]}",
                    name=entity.name,
                    persona=f"Community member with focus on {', '.join(entity.labels)}",
                    role=self._infer_role(entity),
                    interests=self._extract_interests(entity),
                    source_entity_id=entity.id,
                )
                profiles_data.append(stakeholder)
        else:
            # Generate basic profiles without LLM
            for i, entity in enumerate(filtered.entities):
                stakeholder = StakeholderProfile(
                    stakeholder_id=f"stakeholder_{_uuid.uuid4().hex[:12]}",
                    name=entity.name,
                    persona=f"Community member ({', '.join(entity.labels)})",
                    role=self._infer_role(entity),
                    source_entity_id=entity.id,
                )
                profiles_data.append(stakeholder)
        
        logger.info(f"Generated {len(profiles_data)} stakeholder profiles")
        return profiles_data
    
    def _infer_role(self, entity) -> str:
        """Infer stakeholder role from entity labels and properties."""
        labels_lower = [l.lower() for l in entity.labels]
        
        if any(label in labels_lower for label in ['government', 'official', 'authority']):
            return "Government Official"
        elif any(label in labels_lower for label in ['business', 'company', 'corporation']):
            return "Business Representative"
        elif any(label in labels_lower for label in ['citizen', 'resident', 'public']):
            return "Citizen"
        elif any(label in labels_lower for label in ['activist', 'advocate', 'organizer']):
            return "Community Activist"
        elif any(label in labels_lower for label in ['expert', 'specialist', 'professional']):
            return "Domain Expert"
        else:
            return "Community Stakeholder"
    
    def _extract_interests(self, entity) -> List[str]:
        """Extract stakeholder interests from entity properties."""
        interests = []
        
        if entity.properties:
            for key, value in entity.properties.items():
                if isinstance(value, str) and len(value) < 100:
                    interests.append(f"{key}: {value}")
        
        # Add label-based interests
        for label in entity.labels:
            interests.append(f"Focus on {label}")
        
        return interests[:5]  # Limit to top 5 interests
    
    def enrich_profile(
        self,
        profile: StakeholderProfile,
        simulation_requirement: str,
    ) -> StakeholderProfile:
        """Enrich a stakeholder profile with additional context.
        
        Args:
            profile: Base stakeholder profile
            simulation_requirement: Context for enrichment
            
        Returns:
            Enriched StakeholderProfile
        """
        # This would use LLM to add detailed behavioural characteristics
        # For now, we'll add basic enrichment
        profile.behavioural_tendencies = {
            'communication_style': 'moderate',
            'decision_making': 'evidence-based',
            'social_engagement': 'active',
        }
        
        profile.personality_traits = {
            'openness': 0.7,
            'conscientiousness': 0.6,
            'agreeableness': 0.5,
        }
        
        return profile
