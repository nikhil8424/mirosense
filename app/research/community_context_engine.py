"""Community Context Engine - Research layer for community context modeling.

This layer refactors the existing ontology and graph-building functionality
into a research-oriented Community Context Engine. It provides a structured
representation of community entities, relationships, events, stakeholders,
locations, issues, and contextual information.

Foundation: Reuses existing OntologyGenerator and GraphBuilderService.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..services.ontology_generator import OntologyGenerator
from ..services.graph_builder import GraphBuilderService
from ..services.entity_reader import EntityReader
from ..services.graph_db import GraphDatabase
from ..utils.logger import get_logger

logger = get_logger('mirofish.research.community_context')


@dataclass
class CommunityContext:
    """Structured representation of community context."""
    
    context_id: str
    problem_statement: str
    documents: List[str] = field(default_factory=list)
    
    # Entity and relationship information
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    
    # Community-specific information
    stakeholders: List[Dict[str, Any]] = field(default_factory=list)
    locations: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Graph information
    graph_id: Optional[str] = None
    project_id: Optional[str] = None
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Statistics
    entity_count: int = 0
    relationship_count: int = 0
    stakeholder_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'context_id': self.context_id,
            'problem_statement': self.problem_statement,
            'documents': self.documents,
            'entities': self.entities,
            'relationships': self.relationships,
            'stakeholders': self.stakeholders,
            'locations': self.locations,
            'issues': self.issues,
            'events': self.events,
            'graph_id': self.graph_id,
            'project_id': self.project_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'entity_count': self.entity_count,
            'relationship_count': self.relationship_count,
            'stakeholder_count': self.stakeholder_count,
        }


class CommunityContextEngine:
    """Research-oriented Community Context Engine.
    
    This engine provides a structured approach to modeling community context
    from documents, building on the existing MiroFish ontology and graph
    infrastructure.
    
    The engine:
    1. Ingests community documents (PDF, MD, TXT)
    2. Extracts entities and relationships using LLM
    3. Constructs a knowledge graph
    4. Identifies stakeholders, locations, issues, and events
    5. Provides structured community context for simulation
    """
    
    def __init__(
        self,
        ontology_generator: Optional[OntologyGenerator] = None,
        graph_builder: Optional[GraphBuilderService] = None,
        entity_reader: Optional[EntityReader] = None,
        graph_db: Optional[GraphDatabase] = None,
    ):
        self.ontology_generator = ontology_generator or OntologyGenerator()
        self.graph_builder = graph_builder or GraphBuilderService()
        self.entity_reader = entity_reader or EntityReader()
        self.graph_db = graph_db or GraphDatabase()
        logger.info("CommunityContextEngine initialized")
    
    def build_context(
        self,
        problem_statement: str,
        document_texts: List[str],
        context_id: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> CommunityContext:
        """Build community context from documents.
        
        Args:
            problem_statement: The community problem being addressed
            document_texts: List of extracted document texts
            context_id: Optional context identifier
            additional_context: Additional contextual information
            
        Returns:
            CommunityContext: Structured community context
        """
        import uuid as _uuid
        
        if not context_id:
            context_id = f"context_{_uuid.uuid4().hex[:12]}"
        
        logger.info(f"Building community context: {context_id}")
        
        # Step 1: Generate ontology using existing infrastructure
        ontology = self.ontology_generator.generate(
            document_texts=document_texts,
            simulation_requirement=problem_statement,
            additional_context=additional_context,
        )
        
        # Step 2: Create graph using existing infrastructure
        graph_id = self.graph_builder.create_graph(name=f"Context_{context_id}")
        self.graph_builder.set_ontology(graph_id, ontology)
        
        # Step 3: Add text chunks to graph
        from ..services.text_processor import TextProcessor
        chunks = TextProcessor.split_text("\n\n".join(document_texts))
        self.graph_builder.add_text_batches(graph_id, chunks, batch_size=3)
        
        # Step 4: Extract entities and categorize
        filtered = self.entity_reader.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=None,
            enrich_with_edges=True,
        )
        
        # Categorize entities into research-oriented categories
        entities = []
        stakeholders = []
        locations = []
        issues = []
        events = []
        
        for entity in filtered.entities:
            entity_dict = {
                'id': entity.id,
                'name': entity.name,
                'labels': list(entity.labels),
                'summary': entity.summary or '',
                'properties': entity.properties or {},
            }
            entities.append(entity_dict)
            
            # Categorize based on labels and properties
            labels_lower = [l.lower() for l in entity.labels]
            
            if any(label in labels_lower for label in ['person', 'organization', 'group', 'stakeholder']):
                stakeholders.append(entity_dict)
            elif any(label in labels_lower for label in ['location', 'place', 'area', 'region']):
                locations.append(entity_dict)
            elif any(label in labels_lower for label in ['issue', 'problem', 'concern', 'challenge']):
                issues.append(entity_dict)
            elif any(label in labels_lower for label in ['event', 'action', 'incident']):
                events.append(entity_dict)
        
        # Step 5: Extract relationships
        relationships = []
        for edge in filtered.edges:
            relationships.append({
                'source': edge.source,
                'target': edge.target,
                'label': edge.label,
                'properties': edge.properties or {},
            })
        
        # Step 6: Build community context
        context = CommunityContext(
            context_id=context_id,
            problem_statement=problem_statement,
            documents=[],  # Document paths would be added by caller
            entities=entities,
            relationships=relationships,
            stakeholders=stakeholders,
            locations=locations,
            issues=issues,
            events=events,
            graph_id=graph_id,
            entity_count=len(entities),
            relationship_count=len(relationships),
            stakeholder_count=len(stakeholders),
        )
        
        logger.info(
            f"Community context built: {context.entity_count} entities, "
            f"{context.stakeholder_count} stakeholders, "
            f"{context.relationship_count} relationships"
        )
        
        return context
    
    def get_context(self, context_id: str) -> Optional[CommunityContext]:
        """Retrieve existing community context by ID.
        
        Args:
            context_id: Context identifier
            
        Returns:
            CommunityContext if found, None otherwise
        """
        # This would typically retrieve from a context store
        # For now, we'll reconstruct from graph if possible
        logger.warning(f"Context retrieval not fully implemented for {context_id}")
        return None
    
    def update_context(
        self,
        context_id: str,
        additional_documents: List[str] = None,
    ) -> CommunityContext:
        """Update existing community context with new documents.
        
        Args:
            context_id: Context identifier
            additional_documents: Additional document texts to incorporate
            
        Returns:
            Updated CommunityContext
        """
        logger.warning(f"Context update not fully implemented for {context_id}")
        raise NotImplementedError("Context update requires incremental graph building")
