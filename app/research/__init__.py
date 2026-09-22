"""Legacy research package for MiroFish.

.. deprecated:: 0.2.0
    The `app.research` module contains legacy prototype heuristics (including arbitrary
    fixed-weight scoring and mock confidence intervals) and is superseded by the scientifically
    verified `app.mirosense` research extension architecture.
    Please use `app.mirosense` for all research analytics, scenario evaluations, and validations.
"""

import warnings

warnings.warn(
    "The 'app.research' module is deprecated and superseded by 'app.mirosense'.",
    DeprecationWarning,
    stacklevel=2,
)

from .community_context_engine import CommunityContextEngine
from .stakeholder_digital_twin import StakeholderDigitalTwin
from .scenario_designer import ScenarioDesigner, ScenarioManager
from .emergent_behaviour_analyzer import EmergentBehaviourAnalyzer
from .social_impact_model import SocialImpactModel, SocialImpactResult
from .decision_comparison_engine import DecisionComparisonEngine
from .decision_intelligence_engine import DecisionIntelligenceEngine

__all__ = [
    'CommunityContextEngine',
    'StakeholderDigitalTwin',
    'ScenarioDesigner',
    'ScenarioManager',
    'EmergentBehaviourAnalyzer',
    'SocialImpactModel',
    'SocialImpactResult',
    'DecisionComparisonEngine',
    'DecisionIntelligenceEngine',
]
