"""Decision Intelligence Engine - Research layer for decision recommendation.

This layer replaces the existing single report/verdict endpoint with a
comprehensive Decision Intelligence output that includes recommended scenario,
metric comparison, supporting evidence, risks, emergent behaviours, limitations,
and uncertainty quantification.

Foundation: Uses ScenarioComparison from DecisionComparisonEngine.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .decision_comparison_engine import ScenarioComparison
from .social_impact_model import SocialImpactResult
from .emergent_behaviour_analyzer import BehaviourMetrics
from ..utils.logger import get_logger

logger = get_logger('mirofish.research.decision_intelligence')


@dataclass
class DecisionIntelligence:
    """Comprehensive decision intelligence output."""
    
    problem_id: str
    problem_statement: str
    
    # Recommendation
    recommended_scenario_id: Optional[str] = None
    recommended_scenario_name: str = ""
    recommendation_confidence: float = 0.0
    
    # Metric comparison
    metric_comparison: Dict[str, Any] = field(default_factory=dict)
    
    # Supporting evidence
    supporting_evidence: List[str] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    
    # Risk assessment
    major_risks: List[str] = field(default_factory=list)
    risk_summary: str = ""
    
    # Emergent behaviours
    emergent_behaviours: List[str] = field(default_factory=list)
    behaviour_patterns: Dict[str, Any] = field(default_factory=dict)
    
    # Stakeholder reactions
    stakeholder_reactions: List[str] = field(default_factory=list)
    stakeholder_insights: Dict[str, Any] = field(default_factory=dict)
    
    # Limitations and uncertainty
    limitations: List[str] = field(default_factory=list)
    uncertainty_sources: List[str] = field(default_factory=list)
    confidence_intervals: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    simulation_count: int = 0
    total_agent_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'problem_id': self.problem_id,
            'problem_statement': self.problem_statement,
            'recommended_scenario_id': self.recommended_scenario_id,
            'recommended_scenario_name': self.recommended_scenario_name,
            'recommendation_confidence': self.recommendation_confidence,
            'metric_comparison': self.metric_comparison,
            'supporting_evidence': self.supporting_evidence,
            'key_findings': self.key_findings,
            'major_risks': self.major_risks,
            'risk_summary': self.risk_summary,
            'emergent_behaviours': self.emergent_behaviours,
            'behaviour_patterns': self.behaviour_patterns,
            'stakeholder_reactions': self.stakeholder_reactions,
            'stakeholder_insights': self.stakeholder_insights,
            'limitations': self.limitations,
            'uncertainty_sources': self.uncertainty_sources,
            'confidence_intervals': self.confidence_intervals,
            'generated_at': self.generated_at,
            'simulation_count': self.simulation_count,
            'total_agent_count': self.total_agent_count,
        }


class DecisionIntelligenceEngine:
    """Research-oriented Decision Intelligence Engine.
    
    This component provides comprehensive decision intelligence output
    that goes beyond a single verdict to include detailed analysis,
    comparison, evidence, risks, and limitations.
    
    The engine:
    1. Accepts scenario comparison results
    2. Synthesizes supporting evidence
    3. Identifies key findings and emergent behaviours
    4. Assesses risks and stakeholder reactions
    5. Documents limitations and uncertainty
    6. Provides transparent recommendation with confidence
    7. Generates comprehensive decision intelligence output
    
    Note: Intelligence is derived from simulated outcomes and should
    be interpreted as scenario-analysis evidence for decision support,
    not as guaranteed real-world predictions.
    """
    
    def __init__(self):
        logger.info("DecisionIntelligenceEngine initialized")
    
    def generate_intelligence(
        self,
        scenario_comparison: ScenarioComparison,
        behaviour_metrics_map: Optional[Dict[str, BehaviourMetrics]] = None,
    ) -> DecisionIntelligence:
        """Generate comprehensive decision intelligence.
        
        Args:
            scenario_comparison: Scenario comparison results
            behaviour_metrics_map: Optional mapping of scenario_id behaviour metrics
            
        Returns:
            DecisionIntelligence with comprehensive analysis
        """
        logger.info(f"Generating decision intelligence for problem {scenario_comparison.problem_id}")
        
        intelligence = DecisionIntelligence(
            problem_id=scenario_comparison.problem_id,
            problem_statement=scenario_comparison.problem_statement,
            simulation_count=len(scenario_comparison.scenario_results),
            total_agent_count=sum(r.simulation_id and 50 or 0 for r in scenario_comparison.scenario_results),  # Approximate
        )
        
        # Extract recommendation
        intelligence.recommended_scenario_id = scenario_comparison.recommended_scenario_id
        intelligence.recommended_scenario_name = scenario_comparison.recommended_scenario_name
        
        # Calculate recommendation confidence
        if scenario_comparison.scenario_results:
            best_result = next(
                (r for r in scenario_comparison.scenario_results 
                 if r.scenario_id == intelligence.recommended_scenario_id),
                None
            )
            if best_result:
                intelligence.recommendation_confidence = best_result.confidence
        
        # Build metric comparison
        intelligence.metric_comparison = self._build_metric_comparison(scenario_comparison)
        
        # Synthesize supporting evidence
        intelligence.supporting_evidence = self._synthesize_evidence(scenario_comparison)
        intelligence.key_findings = self._extract_key_findings(scenario_comparison)
        
        # Risk assessment
        intelligence.major_risks = self._aggregate_risks(scenario_comparison)
        intelligence.risk_summary = self._summarize_risks(intelligence.major_risks)
        
        # Emergent behaviours
        intelligence.emergent_behaviours = self._identify_emergent_behaviours(
            scenario_comparison,
            behaviour_metrics_map
        )
        intelligence.behaviour_patterns = self._analyze_behaviour_patterns(
            scenario_comparison,
            behaviour_metrics_map
        )
        
        # Stakeholder reactions
        intelligence.stakeholder_reactions = self._infer_stakeholder_reactions(
            scenario_comparison,
            behaviour_metrics_map
        )
        
        # Limitations and uncertainty
        intelligence.limitations = self._document_limitations(scenario_comparison)
        intelligence.uncertainty_sources = self._identify_uncertainty_sources(scenario_comparison)
        intelligence.confidence_intervals = self._estimate_confidence_intervals(scenario_comparison)
        
        logger.info("Decision intelligence generation complete")
        return intelligence
    
    def _build_metric_comparison(
        self,
        comparison: ScenarioComparison,
    ) -> Dict[str, Any]:
        """Build detailed metric comparison."""
        dimensions = [
            'acceptance_score', 'consensus_score', 'polarization_score',
            'conflict_score', 'equity_score', 'adoption_score',
            'stability_score', 'overall_score'
        ]
        
        metric_comparison = {
            'dimensions': {},
            'best_by_dimension': {},
            'worst_by_dimension': {},
        }
        
        for dim in dimensions:
            values = []
            for scenario_id, data in comparison.comparison_table.items():
                if dim in data:
                    values.append({
                        'scenario_id': scenario_id,
                        'scenario_name': data.get('scenario_name', 'Unknown'),
                        'value': data[dim],
                    })
            
            if values:
                values.sort(key=lambda x: x['value'], reverse=True)
                metric_comparison['dimensions'][dim] = values
                metric_comparison['best_by_dimension'][dim] = values[0]
                metric_comparison['worst_by_dimension'][dim] = values[-1]
        
        return metric_comparison
    
    def _synthesize_evidence(
        self,
        comparison: ScenarioComparison,
    ) -> List[str]:
        """Synthesize supporting evidence from comparison."""
        evidence = []
        
        if comparison.ranking_by_overall:
            top = comparison.ranking_by_overall[0]
            evidence.append(
                f"Scenario '{top['scenario_name']}' ranks highest in overall social viability "
                f"with a score of {top['overall_score']:.2f}."
            )
        
        if comparison.ranking_by_acceptance:
            top_acceptance = comparison.ranking_by_acceptance[0]
            evidence.append(
                f"Highest acceptance: '{top_acceptance['scenario_name']}' "
                f"({top_acceptance['score']:.2f})."
            )
        
        if comparison.ranking_by_consensus:
            top_consensus = comparison.ranking_by_consensus[0]
            evidence.append(
                f"Strongest consensus: '{top_consensus['scenario_name']}' "
                f"({top_consensus['score']:.2f})."
            )
        
        if comparison.ranking_by_low_conflict:
            low_conflict = comparison.ranking_by_low_conflict[0]
            evidence.append(
                f"Lowest conflict: '{low_conflict['scenario_name']}' "
                f"({low_conflict['score']:.2f})."
            )
        
        return evidence
    
    def _extract_key_findings(
        self,
        comparison: ScenarioComparison,
    ) -> List[str]:
        """Extract key findings from comparison."""
        findings = []
        
        # Compare top scenarios
        if len(comparison.ranking_by_overall) >= 2:
            top1 = comparison.ranking_by_overall[0]
            top2 = comparison.ranking_by_overall[1]
            score_diff = top1['overall_score'] - top2['overall_score']
            
            if score_diff < 0.1:
                findings.append(
                    f"Top scenarios '{top1['scenario_name']}' and '{top2['scenario_name']}' "
                    f"have similar overall scores ({score_diff:.3f} difference), "
                    "suggesting comparable social viability."
                )
            else:
                findings.append(
                    f"'{top1['scenario_name']}' significantly outperforms '{top2['scenario_name']}' "
                    f"in overall social viability ({score_diff:.3f} difference)."
                )
        
        # Check for polarization patterns
        polarization_values = [
            data.get('polarization_score', 0)
            for data in comparison.comparison_table.values()
        ]
        if polarization_values:
            avg_polarization = sum(polarization_values) / len(polarization_values)
            if avg_polarization > 0.6:
                findings.append(
                    f"High average polarization ({avg_polarization:.2f}) across scenarios "
                    "suggests community division on this issue."
                )
            elif avg_polarization < 0.3:
                findings.append(
                    f"Low average polarization ({avg_polarization:.2f}) across scenarios "
                    "suggests community alignment on this issue."
                )
        
        return findings
    
    def _aggregate_risks(
        self,
        comparison: ScenarioComparison,
    ) -> List[str]:
        """Aggregate risks from all scenarios."""
        all_risks = []
        
        for result in comparison.scenario_results:
            for risk in result.major_risks:
                risk_with_context = f"{result.scenario_name}: {risk}"
                all_risks.append(risk_with_context)
        
        return all_risks
    
    def _summarize_risks(self, risks: List[str]) -> str:
        """Summarize aggregated risks."""
        if not risks:
            return "No significant risks identified across scenarios."
        
        # Categorize risks
        conflict_risks = [r for r in risks if 'conflict' in r.lower()]
        polarization_risks = [r for r in risks if 'polarization' in r.lower()]
        acceptance_risks = [r for r in risks if 'acceptance' in r.lower()]
        
        summary_parts = []
        if conflict_risks:
            summary_parts.append(f"{len(conflict_risks)} scenarios show conflict-related risks")
        if polarization_risks:
            summary_parts.append(f"{len(polarization_risks)} scenarios show polarization-related risks")
        if acceptance_risks:
            summary_parts.append(f"{len(acceptance_risks)} scenarios show acceptance-related risks")
        
        return '. '.join(summary_parts) + '.'
    
    def _identify_emergent_behaviours(
        self,
        comparison: ScenarioComparison,
        behaviour_metrics_map: Optional[Dict[str, BehaviourMetrics]],
    ) -> List[str]:
        """Identify emergent behaviours from metrics."""
        behaviours = []
        
        if not behaviour_metrics_map:
            behaviours.append("Detailed behaviour analysis requires behaviour metrics.")
            return behaviours
        
        for scenario_id, metrics in behaviour_metrics_map.items():
            scenario_name = comparison.comparison_table.get(scenario_id, {}).get('scenario_name', scenario_id)
            
            if metrics.conflict_intensity > 0.5:
                behaviours.append(
                    f"{scenario_name}: High conflict intensity suggests vigorous debate."
                )
            
            if metrics.information_spread_rate > 0.3:
                behaviours.append(
                    f"{scenario_name}: High information diffusion indicates viral content spread."
                )
            
            if metrics.adoption_rate > 0.4:
                behaviours.append(
                    f"{scenario_name}: High adoption rate suggests strong support."
                )
        
        return behaviours if behaviours else ["No significant emergent behaviours identified."]
    
    def _analyze_behaviour_patterns(
        self,
        comparison: ScenarioComparison,
        behaviour_metrics_map: Optional[Dict[str, BehaviourMetrics]],
    ) -> Dict[str, Any]:
        """Analyze behaviour patterns across scenarios."""
        patterns = {
            'sentiment_trends': {},
            'influence_patterns': {},
            'interaction_patterns': {},
        }
        
        if not behaviour_metrics_map:
            return patterns
        
        # Sentiment trends
        for scenario_id, metrics in behaviour_metrics_map.items():
            patterns['sentiment_trends'][scenario_id] = {
                'overall_sentiment': metrics.overall_sentiment,
                'sentiment_distribution': metrics.sentiment_distribution,
            }
        
        # Influence patterns
        for scenario_id, metrics in behaviour_metrics_map.items():
            patterns['influence_patterns'][scenario_id] = {
                'top_influencers': metrics.top_influencers[:3],
                'influence_distribution': metrics.influence_distribution,
            }
        
        return patterns
    
    def _infer_stakeholder_reactions(
        self,
        comparison: ScenarioComparison,
        behaviour_metrics_map: Optional[Dict[str, BehaviourMetrics]],
    ) -> List[str]:
        """Infer stakeholder reactions from metrics."""
        reactions = []
        
        if not behaviour_metrics_map:
            reactions.append("Stakeholder reaction analysis requires behaviour metrics.")
            return reactions
        
        for scenario_id, metrics in behaviour_metrics_map.items():
            scenario_name = comparison.comparison_table.get(scenario_id, {}).get('scenario_name', scenario_id)
            
            if metrics.overall_sentiment > 0.3:
                reactions.append(f"{scenario_name}: Generally positive stakeholder sentiment.")
            elif metrics.overall_sentiment < -0.3:
                reactions.append(f"{scenario_name}: Generally negative stakeholder sentiment.")
            else:
                reactions.append(f"{scenario_name}: Mixed stakeholder sentiment.")
        
        return reactions
    
    def _document_limitations(
        self,
        comparison: ScenarioComparison,
    ) -> List[str]:
        """Document limitations of the analysis."""
        limitations = [
            "Results are based on simulated agent behaviour, not real human responses.",
            "Simulated agents are not equivalent to actual community members.",
            "LLM-based agent behaviour may not capture full complexity of human decision-making.",
            "Simulation parameters (agent count, rounds) may affect results.",
            "Context documents may not capture all relevant community factors.",
        ]
        
        # Add scenario-specific limitations
        for result in comparison.scenario_results:
            if result.confidence < 0.5:
                limitations.append(
                    f"Low confidence for {result.scenario_name} due to limited simulation data."
                )
        
        return limitations
    
    def _identify_uncertainty_sources(
        self,
        comparison: ScenarioComparison,
    ) -> List[str]:
        """Identify sources of uncertainty."""
        uncertainties = [
            "Stochastic nature of LLM agent behaviour",
            "Limited representation of community diversity",
            "Simplified social interaction models",
            "Potential bias in training data of LLMs",
            "Uncertainty in stakeholder representation",
        ]
        
        return uncertainties
    
    def _estimate_confidence_intervals(
        self,
        comparison: ScenarioComparison,
    ) -> Dict[str, Any]:
        """Estimate confidence intervals for key metrics."""
        # This is a heuristic estimate, not a statistical confidence interval
        intervals = {}
        
        for result in comparison.scenario_results:
            intervals[result.scenario_id] = {
                'overall_score_range': [
                    max(0.0, result.overall_score - 0.1),
                    min(1.0, result.overall_score + 0.1),
                ],
                'confidence_level': result.confidence,
            }
        
        return intervals
