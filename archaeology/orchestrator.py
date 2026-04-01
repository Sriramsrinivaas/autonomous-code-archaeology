"""
Code Archaeology Orchestrator - coordinates multi-agent analysis.
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from .analyzer import CodeAnalyzer
from .historian import HistoryAnalyzer
from .debt_assessor import DebtAssessor
from .models import (
    AnalysisResult,
    ArchitecturalDecision,
    DebtItem,
    Recommendation,
)


class ArchaeologyOrchestrator:
    """Orchestrates code archaeology analysis using multiple agents."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.start_time = time.time()

    def run_analysis(self) -> AnalysisResult:
        """Execute full archaeological analysis."""
        print(f"🔍 Starting Code Archaeology Analysis on {self.repo_path}")
        analysis_start = time.time()

        # Initialize result
        result = AnalysisResult(
            repository_path=str(self.repo_path),
            repository_name=self.repo_path.name,
        )

        try:
            # Phase 1: Code Analysis Agent
            print("  ├─ Running Code Analyzer...")
            analyzer = CodeAnalyzer(str(self.repo_path))
            code_graph = analyzer.analyze()
            result.code_graph = code_graph
            
            # Extract patterns
            patterns = analyzer.extract_patterns()
            result.identified_patterns = patterns
            
            print(f"    ├─ Found {len(code_graph.modules)} modules")
            print(f"    └─ Identified {len(patterns)} design patterns")

            # Phase 2: Historian Agent
            print("  ├─ Running Historian Agent...")
            historian = HistoryAnalyzer(str(self.repo_path))
            
            if historian.is_git_repo():
                timeline = historian.extract_timeline()
                top_contributors = historian.extract_top_contributors()
                
                print(f"    ├─ Extracted {len(timeline)} architectural phases")
                print(f"    └─ Top contributors: {', '.join(c[0] for c in top_contributors[:3])}")
                
                # Infer architectural decisions from history
                decisions = self._infer_architectural_decisions(historian, code_graph)
                result.architectural_decisions = decisions
            else:
                print("    └─ Not a git repository, skipping historian analysis")

            # Phase 3: Debt Assessor Agent
            print("  ├─ Running Debt Assessor...")
            assessor = DebtAssessor(str(self.repo_path))
            debt_items = assessor.assess()
            result.tech_debt_items = debt_items
            print(f"    └─ Found {len(debt_items)} debt items")

            # Phase 4: Validator Agent (implicit - scoring)
            print("  ├─ Running Validation...")
            self._validate_findings(result)
            print(f"    └─ Confidence scores assigned")

            # Phase 5: Synthesizer Agent
            print("  ├─ Synthesizing Recommendations...")
            recommendations = self._generate_recommendations(result)
            result.modernization_recommendations = recommendations
            print(f"    └─ Generated {len(recommendations)} recommendations")

            # Compute quality scores
            self._compute_quality_scores(result)

            # Record analysis duration
            result.analysis_duration_seconds = time.time() - analysis_start

            print(f"\n✅ Analysis Complete ({result.analysis_duration_seconds:.1f}s)")
            return result

        except Exception as e:
            print(f"\n❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            result.analysis_duration_seconds = time.time() - analysis_start
            return result

    def _infer_architectural_decisions(
        self, historian: HistoryAnalyzer, code_graph
    ) -> list[ArchitecturalDecision]:
        """Infer architectural decisions from code and history."""
        decisions = []

        # Decision 1: Modularization strategy
        if len(code_graph.modules) > 10:
            decisions.append(ArchitecturalDecision(
                name="Modular Architecture",
                description="Codebase is organized into multiple modules",
                rationale="Separation of concerns for maintainability",
                evidence=[f"Organized into {len(code_graph.modules)} modules"],
                confidence=0.9,
                impact="high"
            ))

        # Decision 2: External dependencies strategy
        if code_graph.external_dependencies:
            decisions.append(ArchitecturalDecision(
                name="External Dependency Usage",
                description=f"Uses {len(code_graph.external_dependencies)} external libraries",
                rationale="Leverage battle-tested libraries instead of reinventing",
                evidence=list(code_graph.external_dependencies)[:5],
                confidence=0.85,
                impact="high"
            ))

        # Decision 3: Circular dependencies handling
        if code_graph.circular_dependencies:
            decisions.append(ArchitecturalDecision(
                name="Circular Dependency Tolerance",
                description="Codebase contains circular dependencies",
                rationale="May indicate tight coupling or architecture issues",
                evidence=[f"{a} ↔ {b}" for a, b in code_graph.circular_dependencies[:3]],
                confidence=0.7,
                impact="medium",
                tradeoffs={
                    "con": "Circular dependencies complicate refactoring",
                    "mitigation": "Consider decoupling or using dependency injection"
                }
            ))

        # Decision 4: Testing strategy (from patterns)
        test_modules = [m for m in code_graph.modules if 'test' in m.lower()]
        if test_modules:
            avg_coverage = sum(m.test_coverage for m in code_graph.modules.values()) / max(1, len(code_graph.modules))
            decisions.append(ArchitecturalDecision(
                name="Testing Strategy",
                description=f"Test coverage estimated at {avg_coverage*100:.0f}%",
                rationale="Testing strategy appears to be in place",
                evidence=[f"{len(test_modules)} test modules found"],
                confidence=0.6,
                impact="medium"
            ))

        return decisions

    def _validate_findings(self, result: AnalysisResult):
        """Validate and score findings."""
        # Check for contradictions
        if result.code_graph and result.code_graph.circular_dependencies:
            if any(d for d in result.architectural_decisions if "Modular" in d.name):
                result.contradictions.append(
                    "Modular architecture claims conflict with circular dependencies"
                )

        # Assign confidence scores
        result.confidence_scores = {
            'architectural_decisions': 0.75,
            'patterns': 0.6,
            'tech_debt': 0.8,
            'recommendations': 0.7,
        }

    def _generate_recommendations(self, result: AnalysisResult) -> list[Recommendation]:
        """Generate modernization recommendations."""
        recommendations = []

        # Recommendation 1: Clean up tech debt
        if result.tech_debt_items:
            high_severity_items = [d for d in result.tech_debt_items if d.severity == 'high']
            if high_severity_items:
                recommendations.append(Recommendation(
                    id="rec_001",
                    category="debt_cleanup",
                    title="Address High-Severity Technical Debt",
                    description=f"Fix {len(high_severity_items)} high-severity debt items",
                    rationale="Reduces maintenance burden and improves stability",
                    estimated_effort="high",
                    priority="high",
                    quick_win=False,
                    related_debt=[d.id for d in high_severity_items[:5]],
                    confidence=0.85
                ))

            # Recommendation 2: Eliminate dead code
            dead_code = [d for d in result.tech_debt_items if d.type.value == 'dead_code']
            if dead_code:
                recommendations.append(Recommendation(
                    id="rec_002",
                    category="refactor",
                    title="Remove Dead Code",
                    description=f"Eliminate {len(dead_code)} unused functions/classes",
                    rationale="Reduces cognitive load and improves code readability",
                    estimated_effort="low",
                    priority="medium",
                    quick_win=True,
                    related_debt=[d.id for d in dead_code],
                    confidence=0.9
                ))

        # Recommendation 3: Modularization
        if result.code_graph:
            large_modules = [
                m for m in result.code_graph.modules.values()
                if m.size > 10000  # 10kb
            ]
            if large_modules:
                recommendations.append(Recommendation(
                    id="rec_003",
                    category="architecture",
                    title="Break Down Large Modules",
                    description=f"Split {len(large_modules)} large modules into smaller units",
                    rationale="Improves maintainability and reduces coupling",
                    affected_modules=[m.name for m in large_modules],
                    estimated_effort="high",
                    priority="medium",
                    implementation_steps=[
                        "Identify logical boundaries within each large module",
                        "Extract cohesive functionality into separate modules",
                        "Update imports and dependencies",
                        "Run comprehensive tests"
                    ],
                    confidence=0.75
                ))

        # Recommendation 4: Documentation
        recommendations.append(Recommendation(
            id="rec_004",
            category="documentation",
            title="Improve Code Documentation",
            description="Add docstrings and architectural documentation",
            rationale="Accelerates onboarding and reduces misunderstandings",
            estimated_effort="medium",
            priority="medium",
            quick_win=False,
            confidence=0.6
        ))

        return recommendations

    def _compute_quality_scores(self, result: AnalysisResult):
        """Compute quality metrics."""
        if not result.code_graph or not result.code_graph.modules:
            return

        # Architecture quality score
        score = 100.0
        if result.code_graph.circular_dependencies:
            score -= len(result.code_graph.circular_dependencies) * 5
        if result.code_graph.modules:
            avg_complexity = sum(
                sum(f.cyclomatic_complexity for f in m.functions.values())
                for m in result.code_graph.modules.values()
            ) / max(1, sum(len(m.functions) for m in result.code_graph.modules.values()))
            if avg_complexity > 5:
                score -= (avg_complexity - 5) * 2
        result.architecture_quality_score = max(0, min(100, score))

        # Tech debt score (lower is better)
        debt_score = len(result.tech_debt_items) * 5
        result.tech_debt_score = min(100, debt_score)

        # Modularity score
        modularity_score = 100.0
        if result.code_graph.external_dependencies:
            modularity_score -= min(20, len(result.code_graph.external_dependencies) * 0.5)
        if len(result.code_graph.modules) < 3:
            modularity_score -= 20
        result.modularity_score = max(0, modularity_score)

        # Maintainability score
        documented = sum(
            1 for m in result.code_graph.modules.values()
            if m.docstring
        )
        doc_ratio = documented / max(1, len(result.code_graph.modules))
        result.maintainability_score = doc_ratio * 100
