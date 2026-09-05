"""Social Impact Model - Research layer for impact evaluation.

This layer evaluates the social consequences of scenarios across multiple
dimensions: acceptance, consensus, polarization, conflict, equity, adoption,
stability, and information diffusion.

Foundation: Uses metrics from EmergentBehaviourAnalyzer.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import statistics

from .emergent_behaviour_analyzer import BehaviourMetrics
from ..utils.logger import get_logger

logger = get_logger('mirofish.research.social_impact')


@dataclass
class SocialImpactResult:
    """Social impact evaluation result for a scenario."""
    
    scenario_id: str
    scenario_name: str
    
    # Impact dimensions (0-1 scale where applicable)
    acceptance_score: float = 0.0
    consensus_score: float = 0.0
    polarization_score: float = 0.0
    conflict_score: float = 0.0
    equity_score: float = 0.0
    adoption_score: float = 0.0
    stability_score: float = 0.0
    information_diffusion_score: float = 0.0
    
    # Overall assessment
    overall_score: float = 0.0
    confidence: float = 0.0  # Uncertainty measure if calculable
    
    # Risk assessment
    major_risks: List[str] = field(default_factory=list)
    risk_level: str = "medium"  # low, medium, high
    
    # Metadata
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    simulation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'scenario_id': self.scenario_id,
            'scenario_name': self.scenario_name,
            'acceptance_score': self.acceptance_score,
            'consensus_score': self.consensus_score,
            'polarization_score': self.polarization_score,
            'conflict_score': self.conflict_score,
            'equity_score': self.equity_score,
            'adoption_score': self.adoption_score,
            'stability_score': self.stability_score,
            'information_diffusion_score': self.information_diffusion_score,
            'overall_score': self.overall_score,
            'confidence': self.confidence,
            'major_risks': self.major_risks,
            'risk_level': self.risk_level,
            'calculated_at': self.calculated_at,
            'simulation_id': self.simulation_id,
        }


class SocialImpactModel:
    """Research-oriented Social Impact Model.
    
    This component evaluates the social consequences of scenarios across
    multiple dimensions based on simulation behaviour metrics.
    
    The model:
    1. Accepts behaviour metrics from EmergentBehaviourAnalyzer
    2. Calculates impact dimension scores
    3. Assesses overall social viability
    4. Identifies major risks
    5. Provides confidence estimates where possible
    
    Note: Impact scores are derived from simulation data and represent
    simulated outcomes, not real-world predictions.
    """
    
    def __init__(self):
        # Weightings for overall score calculation
        self.dimension_weights = {
            'acceptance': 0.20,
            'consensus': 0.15,
            'polarization': 0.15,  # Lower polarization is better
            'conflict': 0.15,  # Lower conflict is better
            'equity': 0.10,
            'adoption': 0.15,
            'stability': 0.10,
        }
        logger.info("SocialImpactModel initialized")
    
    def evaluate_impact(
        self,
        scenario_id: str,
        scenario_name: str,
        behaviour_metrics: BehaviourMetrics,
        simulation_id: Optional[str] = None,
    ) -> SocialImpactResult:
        """Evaluate social impact for a scenario.
        
        Args:
            scenario_id: Scenario identifier
            scenario_name: Scenario name
            behaviour_metrics: Behaviour metrics from analyzer
            simulation_id: Simulation identifier
            
        Returns:
            SocialImpactResult with impact scores
        """
        logger.info(f"Evaluating social impact for scenario {scenario_id}")
        
        result = SocialImpactResult(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            simulation_id=simulation_id,
        )
        
        # Calculate individual dimension scores
        result.acceptance_score = self._calculate_acceptance(behaviour_metrics)
        result.consensus_score = behaviour_metrics.consensus_score
        result.polarization_score = behaviour_metrics.polarization_score
        result.conflict_score = behaviour_metrics.conflict_intensity
        result.equity_score = self._calculate_equity(behaviour_metrics)
        result.adoption_score = behaviour_metrics.adoption_rate
        result.stability_score = self._calculate_stability(behaviour_metrics)
        result.information_diffusion_score = behaviour_metrics.information_spread_rate
        
        # Calculate overall score
        result.overall_score = self._calculate_overall_score(result)
        
        # Assess risks
        result.major_risks = self._identify_risks(result, behaviour_metrics)
        result.risk_level = self._assess_risk_level(result)
        
        # Confidence estimate (based on sample size)
        result.confidence = self._estimate_confidence(behaviour_metrics)
        
        logger.info(f"Social impact evaluation complete: overall_score={result.overall_score:.2f}")
        return result
    
    def _calculate_acceptance(self, metrics: BehaviourMetrics) -> float:
        """Calculate acceptance score from behaviour metrics."""
        # Acceptance is derived from sentiment and support
        sentiment_factor = (metrics.overall_sentiment + 1) / 2  # Normalize to 0-1
        support_factor = metrics.support_ratio
        
        acceptance = (sentiment_factor * 0.6) + (support_factor * 0.4)
        return min(max(acceptance, 0.0), 1.0)
    
    def _calculate_equity(self, metrics: BehaviourMetrics) -> float:
        """Calculate equity score from behaviour metrics."""
        # Equity is approximated by influence distribution
        # More even distribution = higher equity
        if not metrics.influence_distribution:
            return 0.5  # Neutral if no data
        
        influence_values = list(metrics.influence_distribution.values())
        if not influence_values:
            return 0.5
        
        # Use standard deviation as inverse equity measure
        if len(influence_values) > 1:
            std_dev = statistics.stdev(influence_values)
            equity = 1.0 - min(std_dev, 1.0)  # Lower deviation = higher equity
        else:
            equity = 0.5
        
        return min(max(equity, 0.0), 1.0)
    
    def _calculate_stability(self, metrics: BehaviourMetrics) -> float:
        """Calculate stability score from behaviour metrics."""
        # Stability is inverse of conflict and volatility
        conflict_factor = 1.0 - metrics.conflict_intensity
        polarization_factor = 1.0 - metrics.polarization_score
        
        stability = (conflict_factor * 0.6) + (polarization_factor * 0.4)
        return min(max(stability, 0.0), 1.0)
    
    def _calculate_overall_score(self, result: SocialImpactResult) -> float:
        """Calculate overall social viability score."""
        # Weighted sum of dimensions
        # Note: polarization and conflict are inverted (lower is better)
        scores = {
            'acceptance': result.acceptance_score,
            'consensus': result.consensus_score,
            'polarization': 1.0 - result.polarization_score,  # Invert
            'conflict': 1.0 - result.conflict_score,  # Invert
            'equity': result.equity_score,
            'adoption': result.adoption_score,
            'stability': result.stability_score,
        }
        
        weighted_sum = sum(
            scores[dim] * weight
            for dim, weight in self.dimension_weights.items()
        )
        
        return min(max(weighted_sum, 0.0), 1.0)
    
    def _identify_risks(
        self,
        result: SocialImpactResult,
        metrics: BehaviourMetrics,
    ) -> List[str]:
        """Identify major risks from impact scores."""
        risks = []
        
        if result.conflict_score > 0.7:
            risks.append("High conflict intensity may lead to social tension")
        
        if result.polarization_score > 0.7:
            risks.append("High polarization indicates divided community")
        
        if result.acceptance_score < 0.3:
            risks.append("Low acceptance suggests resistance to intervention")
        
        if result.adoption_score < 0.2:
            risks.append("Low adoption rate may limit effectiveness")
        
        if result.equity_score < 0.3:
            risks.append("Low equity indicates uneven impact distribution")
        
        if metrics.disagreement_count > metrics.sample_size * 0.3:
            risks.append("High disagreement rate may impede implementation")
        
        return risks
    
    def _assess_risk_level(self, result: SocialImpactResult) -> str:
        """Assess overall risk level."""
        risk_count = len(result.major_risks)
        
        if risk_count >= 4:
            return "high"
        elif risk_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _estimate_confidence(self, metrics: BehaviourMetrics) -> float:
        """Estimate confidence in impact assessment.
        
        Confidence is based on sample size and data completeness.
        This is a heuristic measure, not a statistical confidence interval.
        """
        if metrics.sample_size == 0:
            return 0.0
        
        # Confidence increases with sample size (diminishing returns)
        # Using a logarithmic scale
        base_confidence = min(1.0, metrics.sample_size / 100.0)
        
        # Adjust for data completeness
        has_sentiment = metrics.overall_sentiment != 0
        has_influence = len(metrics.influence_distribution) > 0
        completeness_factor = (1 + has_sentiment + has_influence) / 3
        
        confidence = base_confidence * completeness_factor
        return min(max(confidence, 0.0), 1.0)
    
    def compare_impacts(
        self,
        impact_results: List[SocialImpactResult],
    ) -> Dict[str, Any]:
        """Compare social impact across multiple scenarios.
        
        Args:
            impact_results: List of SocialImpactResult objects
            
        Returns:
            Comparison summary
        """
        logger.info(f"Comparing social impact across {len(impact_results)} scenarios")
        
        comparison = {
            'scenario_count': len(impact_results),
            'scenarios': [],
            'rankings': {},
        }
        
        # Build comparison table
        dimensions = [
            'acceptance_score', 'consensus_score', 'polarization_score',
            'conflict_score', 'equity_score', 'adoption_score',
            'stability_score', 'overall_score'
        ]
        
        for result in impact_results:
            comparison['scenarios'].append(result.to_dict())
        
        # Rank by overall score
        sorted_results = sorted(impact_results, key=lambda r: r.overall_score, reverse=True)
        comparison['rankings']['by_overall_score'] = [
            {'scenario_id': r.scenario_id, 'scenario_name': r.scenario_name, 'score': r.overall_score}
            for r in sorted_results
        ]
        
        # Dimension rankings
        for dim in dimensions:
            sorted_by_dim = sorted(impact_results, key=lambda r: getattr(r, dim), reverse=True)
            comparison['rankings'][f'by_{dim}'] = [
                {'scenario_id': r.scenario_id, 'score': getattr(r, dim)}
                for r in sorted_by_dim
            ]
        
        return comparison
