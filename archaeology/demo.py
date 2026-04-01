#!/usr/bin/env python3
"""
Demo and test script for Code Archaeology Agent.
Runs analysis on the current codebase.
"""

import sys
from pathlib import Path

# Add parent to path to allow relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from archaeology import ArchaeologyOrchestrator
from archaeology.reporter import ReportGenerator


def main():
    """Run archaeology analysis on the current project."""
    
    # Analyze the sri-claude repository itself
    repo_path = Path(__file__).parent.parent.parent  # root of repo
    
    print("=" * 60)
    print("Code Archaeology Agent - Demo Analysis")
    print("=" * 60)
    print()
    
    # Run analysis
    orchestrator = ArchaeologyOrchestrator(str(repo_path))
    result = orchestrator.run_analysis()
    
    print()
    print("=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print()
    
    # Summary
    print(f"Repository: {result.repository_name}")
    print(f"Location: {result.repository_path}")
    print(f"Analysis Time: {result.analysis_duration_seconds:.1f}s")
    print()
    
    # Scores
    print("Quality Scores:")
    print(f"  • Architecture Quality:  {result.architecture_quality_score:6.1f}/100")
    print(f"  • Modularity Score:      {result.modularity_score:6.1f}/100")
    print(f"  • Maintainability:       {result.maintainability_score:6.1f}/100")
    print(f"  • Tech Debt Level:       {result.tech_debt_score:6.1f}/100")
    print()
    
    # Code structure
    if result.code_graph:
        print(f"Code Structure:")
        print(f"  • Modules: {len(result.code_graph.modules)}")
        print(f"  • Classes: {sum(len(m.classes) for m in result.code_graph.modules.values())}")
        print(f"  • Functions: {sum(len(m.functions) for m in result.code_graph.modules.values())}")
        print(f"  • External Dependencies: {len(result.code_graph.external_dependencies)}")
        if result.code_graph.circular_dependencies:
            print(f"  • Circular Dependencies: {len(result.code_graph.circular_dependencies)}")
        print()
    
    # Findings
    if result.identified_patterns:
        print(f"Design Patterns: {len(result.identified_patterns)} identified")
        print(f"  • {', '.join(result.identified_patterns[:5])}")
        print()
    
    if result.architectural_decisions:
        print(f"Architectural Decisions: {len(result.architectural_decisions)}")
        for i, decision in enumerate(result.architectural_decisions[:3], 1):
            print(f"  {i}. {decision.name} (confidence: {decision.confidence*100:.0f}%)")
        print()
    
    if result.tech_debt_items:
        print(f"Technical Debt Identified: {len(result.tech_debt_items)} items")
        high = len([d for d in result.tech_debt_items if d.severity == 'high'])
        medium = len([d for d in result.tech_debt_items if d.severity == 'medium'])
        low = len([d for d in result.tech_debt_items if d.severity == 'low'])
        print(f"  • High: {high}, Medium: {medium}, Low: {low}")
        print()
    
    if result.modernization_recommendations:
        print(f"Recommendations: {len(result.modernization_recommendations)}")
        quick_wins = [r for r in result.modernization_recommendations if r.quick_win]
        print(f"  • Quick Wins: {len(quick_wins)}")
        for rec in quick_wins[:2]:
            print(f"    - {rec.title}")
        print()
    
    # Generate and save report
    report_dir = repo_path / '.archaeology_reports'
    saved = ReportGenerator.save_report(result, report_dir, formats=['md', 'json'])
    
    print("=" * 60)
    print("Reports Generated:")
    for fmt, path in saved.items():
        print(f"  • {fmt.upper()}: {path.relative_to(repo_path)}")
    print()
    
    # Print snippet of markdown
    if 'markdown' in saved:
        print("=" * 60)
        print("MARKDOWN REPORT PREVIEW")
        print("=" * 60)
        md_content = ReportGenerator.to_markdown(result)
        # Print first 2000 chars
        print(md_content[:2000])
        print("\n... (see full report in file)")
    

if __name__ == '__main__':
    main()
