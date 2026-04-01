"""
Report generation for archaeology analysis results.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import AnalysisResult, DebtType


class ReportGenerator:
    """Generates human-readable reports from analysis results."""

    @staticmethod
    def to_markdown(result: AnalysisResult) -> str:
        """Generate markdown report."""
        lines = [
            f"# Code Archaeology Report: {result.repository_name}",
            "",
            f"**Analyzed:** {result.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Location:** {result.repository_path}  ",
            f"**Duration:** {result.analysis_duration_seconds:.1f}s",
            "",
        ]

        # Executive Summary
        lines.extend([
            "## 📊 Executive Summary",
            "",
            f"| Metric | Score |",
            f"|--------|-------|",
            f"| Architecture Quality | {result.architecture_quality_score:.0f}/100 |",
            f"| Modularity | {result.modularity_score:.0f}/100 |",
            f"| Maintainability | {result.maintainability_score:.0f}/100 |",
            f"| Tech Debt Level | {result.tech_debt_score:.0f}/100 |",
            "",
        ])

        # Architectural Decisions
        if result.architectural_decisions:
            lines.extend([
                "## 🏗️ Architectural Decisions",
                ""
            ])
            for decision in result.architectural_decisions:
                lines.extend([
                    f"### {decision.name}",
                    f"**Description:** {decision.description}  ",
                    f"**Rationale:** {decision.rationale}  ",
                    f"**Confidence:** {decision.confidence*100:.0f}%  ",
                    f"**Impact:** {decision.impact}",
                    ""
                ])
                if decision.evidence:
                    lines.extend([
                        "**Evidence:**",
                        *[f"- {e}" for e in decision.evidence[:3]],
                        ""
                    ])

        # Design Patterns
        if result.identified_patterns:
            lines.extend([
                "## 🎨 Design Patterns",
                ""
            ])
            # Group by pattern type
            pattern_groups = {}
            for pattern in result.identified_patterns:
                pattern_type = pattern.split(':')[0]
                if pattern_type not in pattern_groups:
                    pattern_groups[pattern_type] = []
                pattern_groups[pattern_type].append(pattern)
            
            for pattern_type, patterns in pattern_groups.items():
                lines.append(f"### {pattern_type.title()}")
                lines.extend([f"- {p}" for p in patterns[:5]])
                lines.append("")

        # Technical Debt
        if result.tech_debt_items:
            lines.extend([
                "## 🚨 Technical Debt",
                ""
            ])
            
            # Group by severity
            by_severity = {'high': [], 'medium': [], 'low': []}
            for item in result.tech_debt_items:
                by_severity[item.severity].append(item)
            
            for severity in ['high', 'medium', 'low']:
                items = by_severity.get(severity, [])
                if items:
                    lines.append(f"### {severity.upper()} Severity ({len(items)} items)")
                    lines.append("")
                    for item in items[:5]:
                        lines.extend([
                            f"- **{item.type.value}** in {item.location}",
                            f"  - {item.description}",
                            f"  - Confidence: {item.confidence*100:.0f}%",
                            ""
                        ])

        # Recommendations
        if result.modernization_recommendations:
            lines.extend([
                "## 💡 Recommendations",
                ""
            ])
            
            # High priority first
            high_pri = [r for r in result.modernization_recommendations if r.priority == 'high']
            medium_pri = [r for r in result.modernization_recommendations if r.priority == 'medium']
            
            for priority, recs in [('High', high_pri), ('Medium', medium_pri)]:
                if recs:
                    lines.append(f"### {priority} Priority")
                    lines.append("")
                    for rec in recs[:3]:
                        lines.extend([
                            f"#### {rec.title}",
                            f"**Category:** {rec.category}  ",
                            f"**Effort:** {rec.estimated_effort}  ",
                            f"**Quick Win:** {'Yes' if rec.quick_win else 'No'}  ",
                            f"**Confidence:** {rec.confidence*100:.0f}%",
                            "",
                            rec.description,
                            "",
                            f"**Rationale:** {rec.rationale}",
                            ""
                        ])
                        if rec.implementation_steps:
                            lines.append("**Implementation Steps:**")
                            lines.extend([f"{i+1}. {step}" for i, step in enumerate(rec.implementation_steps)])
                            lines.append("")

        # Contradictions
        if result.contradictions:
            lines.extend([
                "## ⚠️ Findings & Contradictions",
                ""
            ])
            for contradiction in result.contradictions:
                lines.append(f"- {contradiction}")
            lines.append("")

        lines.extend([
            "---",
            f"*Report generated by Code Archaeology Agent*",
        ])

        return "\n".join(lines)

    @staticmethod
    def to_json(result: AnalysisResult) -> dict:
        """Generate JSON report."""
        return result.to_json_friendly()

    @staticmethod
    def save_report(result: AnalysisResult, output_dir: Path, formats: list[str] = None) -> dict[str, Path]:
        """Save report in multiple formats."""
        if formats is None:
            formats = ['md', 'json']
        
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = result.analyzed_at.strftime('%Y%m%d_%H%M%S')
        repo_name = result.repository_name.replace('/', '_').replace('\\', '_')
        
        saved_files = {}
        
        # Markdown report
        if 'md' in formats:
            md_path = output_dir / f"archaeology_{repo_name}_{timestamp}.md"
            md_path.write_text(ReportGenerator.to_markdown(result), encoding='utf-8')
            saved_files['markdown'] = md_path
        
        # JSON report
        if 'json' in formats:
            import json
            json_path = output_dir / f"archaeology_{repo_name}_{timestamp}.json"
            json_path.write_text(json.dumps(result.to_json_friendly(), indent=2), encoding='utf-8')
            saved_files['json'] = json_path
        
        return saved_files
