"""
Data structures for code archaeology analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class Confidence(Enum):
    """Confidence level for findings."""
    HIGH = 0.8
    MEDIUM = 0.5
    LOW = 0.2


class PatternType(Enum):
    """Types of design patterns."""
    SINGLETON = "singleton"
    FACTORY = "factory"
    OBSERVER = "observer"
    STRATEGY = "strategy"
    ADAPTER = "adapter"
    DECORATOR = "decorator"
    FACADE = "facade"
    PROXY = "proxy"
    STATE = "state"
    MVC = "mvc"
    COMMAND = "command"
    OTHER = "other"


class DebtType(Enum):
    """Types of technical debt."""
    OUTDATED_DEPENDENCY = "outdated_dependency"
    DEAD_CODE = "dead_code"
    DUPLICATION = "duplication"
    LEGACY_PATTERN = "legacy_pattern"
    POOR_MODULARITY = "poor_modularity"
    INADEQUATE_TESTING = "inadequate_testing"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DOCUMENTATION = "documentation"


@dataclass
class FunctionDef:
    """Function/method definition."""
    name: str
    module: str
    class_name: Optional[str] = None
    params: list[str] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    cyclomatic_complexity: int = 1
    line_count: int = 0
    is_public: bool = True
    calls: list[str] = field(default_factory=list)
    called_by: list[str] = field(default_factory=list)


@dataclass
class ClassDef:
    """Class definition."""
    name: str
    module: str
    bases: list[str] = field(default_factory=list)
    methods: dict[str, FunctionDef] = field(default_factory=dict)
    properties: list[str] = field(default_factory=list)
    docstring: Optional[str] = None
    is_public: bool = True
    line_count: int = 0


@dataclass
class Module:
    """Python module/file."""
    path: str
    name: str
    size: int
    imports: list[str] = field(default_factory=list)
    imported_by: list[str] = field(default_factory=list)
    classes: dict[str, ClassDef] = field(default_factory=dict)
    functions: dict[str, FunctionDef] = field(default_factory=dict)
    docstring: Optional[str] = None
    test_coverage: float = 0.0


@dataclass
class CodeGraph:
    """Complete code structure graph."""
    root_path: str
    modules: dict[str, Module] = field(default_factory=dict)
    all_imports: dict[str, set[str]] = field(default_factory=dict)
    circular_dependencies: list[tuple[str, str]] = field(default_factory=list)
    external_dependencies: set[str] = field(default_factory=set)
    built_at: datetime = field(default_factory=datetime.now)


@dataclass
class ArchitecturalDecision:
    """Identified architectural decision."""
    name: str
    description: str
    rationale: str
    tradeoffs: dict[str, str] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.5
    impact: str = "medium"  # low, medium, high
    alternatives: list[str] = field(default_factory=list)


@dataclass
class DebtItem:
    """Identified technical debt."""
    id: str
    type: DebtType
    location: str  # file:line or module
    description: str
    severity: str = "medium"  # low, medium, high
    impact: Optional[str] = None
    remediation_effort: Optional[str] = None  # low, medium, high
    confidence: float = 0.5
    evidence: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """Modernization recommendation."""
    id: str
    category: str  # "dependency", "architecture", "refactor", "testing", etc.
    title: str
    description: str
    rationale: str
    affected_modules: list[str] = field(default_factory=list)
    estimated_effort: str = "medium"  # low, medium, high
    priority: str = "medium"  # low, medium, high
    implementation_steps: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    confidence: float = 0.5
    related_debt: list[str] = field(default_factory=list)
    quick_win: bool = False


@dataclass
class AnalysisResult:
    """Complete archaeology analysis result."""
    repository_path: str
    repository_name: str
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    # Analysis components
    code_graph: Optional[CodeGraph] = None
    metrics: dict[str, Any] = field(default_factory=dict)
    
    # Findings
    architectural_decisions: list[ArchitecturalDecision] = field(default_factory=list)
    identified_patterns: list[str] = field(default_factory=list)
    tech_debt_items: list[DebtItem] = field(default_factory=list)
    modernization_recommendations: list[Recommendation] = field(default_factory=list)
    
    # Quality assessment
    architecture_quality_score: float = 0.0  # 0-100
    tech_debt_score: float = 0.0  # 0-100 (lower is better)
    modularity_score: float = 0.0  # 0-100
    maintainability_score: float = 0.0  # 0-100
    
    # Validation
    confidence_scores: dict[str, float] = field(default_factory=dict)
    contradictions: list[str] = field(default_factory=list)
    analysis_duration_seconds: float = 0.0
    
    def to_json_friendly(self) -> dict[str, Any]:
        """Convert to JSON-serializable format."""
        return {
            'repository_path': self.repository_path,
            'repository_name': self.repository_name,
            'analyzed_at': self.analyzed_at.isoformat(),
            'metrics': self.metrics,
            'architectural_decisions': [
                {
                    'name': d.name,
                    'description': d.description,
                    'rationale': d.rationale,
                    'confidence': d.confidence,
                    'impact': d.impact,
                }
                for d in self.architectural_decisions
            ],
            'tech_debt_items': [
                {
                    'id': d.id,
                    'type': d.type.value,
                    'location': d.location,
                    'description': d.description,
                    'severity': d.severity,
                    'confidence': d.confidence,
                }
                for d in self.tech_debt_items
            ],
            'recommendations': [
                {
                    'id': r.id,
                    'category': r.category,
                    'title': r.title,
                    'description': r.description,
                    'priority': r.priority,
                    'estimated_effort': r.estimated_effort,
                    'quick_win': r.quick_win,
                }
                for r in self.modernization_recommendations
            ],
            'scores': {
                'architecture_quality': self.architecture_quality_score,
                'tech_debt': self.tech_debt_score,
                'modularity': self.modularity_score,
                'maintainability': self.maintainability_score,
            },
            'analysis_duration_seconds': self.analysis_duration_seconds,
        }
