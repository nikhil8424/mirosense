"""Decision Comparison Engine - Research layer for scenario comparison.

This component compares multiple candidate decisions based on their social
impact metrics and provides ranking and recommendation.

Foundation: Uses SocialImpactResult from SocialImpactModel.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from .social_impact_model import SocialImpactResult
from ..utils.logger import get_logger

logger = get_logger('mirofish.research.decision_comparison')


@dataclass
class ScenarioComparison:
    """Comparison result for multiple scenarios."""
    
    problem_id: str
    problem_statement: str
    
    # Scenario results
    scenario_results: List[SocialImpactResult] = field(default_factory=list)
    
    # Rankings
    ranking_by_overall: List[Dict[str, Any]] = field(default_factory=list)
    ranking_by_acceptance: List[Dict[str, Any]] = field(default_factory=list)
    ranking_by_consensus: List[Dict[str, Any]] = field(default_factory=list)
    ranking_by_low_conflict: List[Dict[str, Any]] = field(default_factory=list)
    
    # Recommendation
    recommended_scenario_id: Optional[str] = None
    recommended_scenario_name: str = ""
    recommendation_rationale: str = ""
    
    # Comparison table
    comparison_table: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Metadata
    compared_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'problem_id': self.problem_id,
            'problem_statement': self.problem_statement,
            'scenario_count': len(self.scenario_results),
            'scenario_results': [r.to_dict() for r in self.scenario_results],
            'ranking_by_overall': self.ranking_by_overall,
            'ranking_by_acceptance': self.ranking_by_acceptance,
            'ranking_by_consensus': self.ranking_by_consensus,
            'ranking_by_low_conflict': self.ranking_by_low_conflict,
            'recommended_scenario_id': self.recommended_scenario_id,
            'recommended_scenario_name': self.recommended_scenario_name,
            'recommendation_rationale': self.recommendation_rationale,
            'comparison_table': self.comparison_table,
            'compared_at': self.compared_at,
        }


class DecisionComparisonEngine:
    """Research-oriented Decision Comparison Engine.
    
    This component compares multiple candidate decisions based on their
    social impact metrics and provides ranking and recommendation.
    
    The engine:
    1. Accepts social impact results for multiple scenarios
    2. Generates comparison tables across dimensions
    3. Ranks scenarios by different criteria
    4. Identifies the most socially viable option
    5. Provides recommendation rationale
    6. Exposes individual metric values for transparency
    
    Note: Recommendations are based on simulated outcomes and should
    be interpreted as scenario-analysis evidence, not real-world predictions.
    """
    
    def __init__(self):
        logger.info("DecisionComparisonEngine initialized")
    
    def compare_scenarios(
        self,
        problem_id: str,
        problem_statement: str,
        impact_results: List[SocialImpactResult],
    ) -> ScenarioComparison:
        """Compare multiple scenarios for a decision problem.
        
        Args:
            problem_id: Problem identifier
            problem_statement: The community problem being addressed
            impact_results: List of social impact results for scenarios
            
        Returns:
            ScenarioComparison with rankings and recommendation
        """
        logger.info(f"Comparing {len(impact_results)} scenarios for problem {problem_id}")
        
        comparison = ScenarioComparison(
            problem_id=problem_id,
            problem_statement=problem_statement,
            scenario_results=impact_results,
        )
        
        # Build comparison table
        comparison.comparison_table = self._build_comparison_table(impact_results)
        
        # Generate rankings
        comparison.ranking_by_overall = self._rank_by_overall(impact_results)
        comparison.ranking_by_acceptance = self._rank_by_dimension(impact_results, 'acceptance_score')
        comparison.ranking_by_consensus = self._rank_by_dimension(impact_results, 'consensus_score')
        comparison.ranking_by_low_conflict = self._rank_by_dimension(impact_results, 'conflict_score', reverse=True)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(impact_results, comparison)
        comparison.recommended_scenario_id = recommendation['scenario_id']
        comparison.recommended_scenario_name = recommendation['scenario_name']
        comparison.recommendation_rationale = recommendation['rationale']
        
        logger.info(f"Comparison complete: recommended {comparison.recommended_scenario_name}")
        return comparison
    
    def _build_comparison_table(
        self,
        impact_results: List[SocialImpactResult],
    ) -> Dict[str, Dict[str, float]]:
        """Build a comparison table across all dimensions."""
        dimensions = [
            'acceptance_score', 'consensus_score', 'polarization_score',
            'conflict_score', 'equity_score', 'adoption_score',
            'stability_score', 'overall_score'
        ]
        
        table = {}
        for result in impact_results:
            table[result.scenario_id] = {
                'scenario_name': result.scenario_name,
                **{dim: getattr(result, dim) for dim in dimensions}
            }
        
        return table
    
    def _rank_by_overall(
        self,
        impact_results: List[SocialImpactResult],
    ) -> List[Dict[str, Any]]:
        """Rank scenarios by overall social viability score."""
        sorted_results = sorted(impact_results, key=lambda r: r.overall_score, reverse=True)
        
        return [
            {
                'rank': i + 1,
                'scenario_id': r.scenario_id,
                'scenario_name': r.scenario_name,
                'overall_score': r.overall_score,
                'confidence': r.confidence,
            }
            for i, r in enumerate(sorted_results)
        ]
    
    def _rank_by_dimension(
        self,
        impact_results: List[SocialImpactResult],
        dimension: str,
        reverse: bool = True,
    ) -> List[Dict[str, Any]]:
        """Rank scenarios by a specific dimension."""
        sorted_results = sorted(
            impact_results,
            key=lambda r: getattr(r, dimension),
            reverse=reverse
        )
        
        return [
            {
                'rank': i + 1,
                'scenario_id': r.scenario_id,
                'scenario_name': r.scenario_name,
                'score': getattr(r, dimension),
            }
            for i, r in enumerate(sorted_results)
        ]
    
    def _generate_recommendation(
        self,
        impact_results: List[SocialImpactResult],
        comparison: ScenarioComparison,
    ) -> Dict[str, str]:
        """Generate recommendation with rationale."""
        if not impact_results:
            return {
                'scenario_id': None,
                'scenario_name': 'No scenarios available',
                'rationale': 'No scenarios to compare.',
            }
        
        # Select scenario with highest overall score
        best_scenario = max(impact_results, key=lambda r: r.overall_score)
        
        # Build rationale
        rationale_parts = []
        
        rationale_parts.append(
            f"{best_scenario.scenario_name} has the highest overall social viability score "
            f"({best_scenario.overall_score:.2f})."
        )
        
        # Highlight strengths
        strengths = []
        if best_scenario.acceptance_score > 0.7:
            strengths.append(f"high acceptance ({best_scenario.acceptance_score:.2f})")
        if best_scenario.consensus_score > 0.7:
            strengths.append(f"strong consensus ({best_scenario.consensus_score:.2f})")
        if best_scenario.conflict_score < 0.3:
            strengths.append(f"low conflict ({best_scenario.conflict_score:.2f})")
        if best_scenario.equity_score > 0.7:
            strengths.append(f"high equity ({best_scenario.equity_score:.2f})")
        
        if strengths:
            rationale_parts.append(f"Key strengths: {', '.join(strengths)}.")
        
        # Note risks
        if best_scenario.major_risks:
            rationale_parts.append(
                f"However, consider the identified risks: {', '.join(best_scenario.major_risks[:2])}."
            )
        
        # Add confidence note
        if best_scenario.confidence < 0.5:
            rationale_parts.append(
                f"Note: Confidence in this assessment is moderate ({best_scenario.confidence:.2f}) "
                "due to limited simulation data."
            )
        
        # Add disclaimer
        rationale_parts.append(
            "This recommendation is based on simulated outcomes under the specified conditions "
            "and should be interpreted as scenario-analysis evidence rather than a guaranteed real-world prediction."
        )
        
        rationale = ' '.join(rationale_parts)
        
        return {
            'scenario_id': best_scenario.scenario_id,
            'scenario_name': best_scenario.scenario_name,
            'rationale': rationale,
        }
    
    def get_dimension_comparison(
        self,
        comparison: ScenarioComparison,
        dimension: str,
    ) -> Dict[str, Any]:
        """Get detailed comparison for a specific dimension.
        
        Args:
            comparison: ScenarioComparison object
            dimension: Dimension name (e.g., 'acceptance_score')
            
        Returns:
            Dimension-specific comparison
        """
        values = []
        for scenario_id, data in comparison.comparison_table.items():
            if dimension in data:
                values.append({
                    'scenario_id': scenario_id,
                    'scenario_name': data.get('scenario_name', 'Unknown'),
                    'value': data[dimension],
                })
        
        # Sort by value
        values.sort(key=lambda x: x['value'], reverse=True)
        
        return {
            'dimension': dimension,
            'scenarios': values,
            'best': values[0] if values else None,
            'worst': values[-1] if values else None,
        }
