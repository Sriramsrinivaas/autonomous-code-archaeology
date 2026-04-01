"""
Command-line interface for Code Archaeology Agent.
"""

import argparse
import json
from pathlib import Path

from .orchestrator import ArchaeologyOrchestrator
from .reporter import ReportGenerator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Autonomous Code Archaeology Agent - analyze codebases for architectural insights'
    )
    
    parser.add_argument(
        'repository',
        help='Path to the repository to analyze'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        type=Path,
        default=Path('.archaeology_reports'),
        help='Output directory for reports (default: .archaeology_reports)'
    )
    
    parser.add_argument(
        '--format',
        '-f',
        choices=['md', 'json', 'both'],
        default='both',
        help='Report format (default: both)'
    )
    
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Suppress progress output'
    )
    
    args = parser.parse_args()
    
    repo_path = Path(args.repository).resolve()
    if not repo_path.exists():
        print(f"❌ Repository not found: {repo_path}")
        return 1
    
    # Run analysis
    orchestrator = ArchaeologyOrchestrator(str(repo_path))
    result = orchestrator.run_analysis()
    
    # Determine formats
    formats = ['md', 'json'] if args.format == 'both' else [args.format]
    
    # Save reports
    saved = ReportGenerator.save_report(result, args.output, formats=formats)
    
    if not args.quiet:
        print(f"\n📄 Reports saved to {args.output}:")
        for fmt, path in saved.items():
            print(f"  • {fmt.upper()}: {path}")
    
    return 0


def analyze_repository(repo_path: str, output_dir: str = '.archaeology_reports') -> dict:
    """
    Programmatic interface for running archaeology analysis.
    
    Args:
        repo_path: Path to repository
        output_dir: Directory to save reports
    
    Returns:
        Dictionary with analysis results and report paths
    """
    orchestrator = ArchaeologyOrchestrator(repo_path)
    result = orchestrator.run_analysis()
    
    saved = ReportGenerator.save_report(
        result,
        Path(output_dir),
        formats=['md', 'json']
    )
    
    return {
        'result': result,
        'reports': saved,
        'scores': {
            'architecture_quality': result.architecture_quality_score,
            'modularity': result.modularity_score,
            'maintainability': result.maintainability_score,
            'tech_debt': result.tech_debt_score,
        },
        'summary': {
            'total_modules': len(result.code_graph.modules) if result.code_graph else 0,
            'architectural_decisions': len(result.architectural_decisions),
            'design_patterns': len(result.identified_patterns),
            'tech_debt_items': len(result.tech_debt_items),
            'recommendations': len(result.modernization_recommendations),
        }
    }


if __name__ == '__main__':
    exit(main())
