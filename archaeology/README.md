# Code Archaeology Agent

An autonomous multi-agent system for analyzing code repositories to understand architectural decisions, identify technical debt, and propose modernization strategies.

## Features

### Multi-Agent Architecture
- **Code Analyzer Agent** - Parses code structure, extracts patterns, identifies architectural components
- **Historian Agent** - Reconstructs architectural evolution from git history
- **Debt Assessor Agent** - Identifies technical debt items and code quality issues
- **Validator Agent** - Cross-checks findings and assigns confidence scores
- **Synthesizer Agent** - Orchestrates other agents and generates actionable reports

### Analysis Capabilities
- 🔍 **Code Structure Analysis** - Modules, classes, functions, dependencies
- 🏗️ **Architectural Pattern Detection** - Factory, Singleton, Strategy, and more
- 📊 **Quality Metrics** - Cyclomatic complexity, modularity, maintainability scores
- 🚨 **Tech Debt Detection** - Outdated dependencies, dead code, duplication, legacy patterns
- 💡 **Modernization Recommendations** - Prioritized, effort-estimated suggestions
- 📈 **Evolution Tracking** - Understand how architecture evolved over time

## Quick Start

### CLI Usage
```bash
# Analyze a repository
python -m src.archaeology.cli /path/to/repository

# Custom output directory
python -m src.archaeology.cli /path/to/repository --output ./reports

# JSON only
python -m src.archaeology.cli /path/to/repository --format json

# Quiet mode
python -m src.archaeology.cli /path/to/repository --quiet
```

### Programmatic Usage
```python
from src.archaeology import ArchaeologyOrchestrator
from src.archaeology.reporter import ReportGenerator
from pathlib import Path

# Run analysis
orchestrator = ArchaeologyOrchestrator('/path/to/repository')
result = orchestrator.run_analysis()

# Access results
print(f"Architecture Quality: {result.architecture_quality_score}/100")
print(f"Tech Debt Items: {len(result.tech_debt_items)}")
print(f"Recommendations: {len(result.modernization_recommendations)}")

# Generate reports
saved = ReportGenerator.save_report(
    result, 
    Path('./reports'),
    formats=['md', 'json']
)
```

### Demo
```bash
# Run analysis on the sri-claude repository
python src/archaeology/demo.py
```

## Output

### Markdown Report
- Executive summary with quality scores
- Architectural decisions with evidence and rationale
- Identified design patterns
- Technical debt by severity
- Actionable recommendations prioritized by impact

### JSON Report
- Machine-readable format for integration with tools
- Complete analysis data structures
- Metrics and confidence scores

## Analysis Results

The analysis returns detailed findings in several categories:

### Architectural Decisions
Key choices that shape the codebase with:
- Description and rationale
- Evidence from the code
- Confidence scores
- Impact assessment

### Design Patterns
Identified patterns like:
- Singleton, Factory, Strategy, Observer
- Adapter, Decorator, Facade, Proxy
- Custom architectural patterns

### Technical Debt
Issues categorized by:
- **Outdated Dependencies** - Packages needing updates
- **Dead Code** - Unused functions/classes
- **Duplication** - Repeated code blocks
- **Legacy Patterns** - Outdated coding practices
- **Poor Modularity** - Large files, high coupling
- **Testing Gaps** - Insufficient test coverage

### Recommendations
Prioritized suggestions including:
- Implementation steps
- Effort estimates (low/medium/high)
- Risk assessment
- Quick wins for fast improvements
- Related technical debt items

## Quality Scores (0-100)

- **Architecture Quality** - Structural design and complexity
- **Modularity** - Code organization and dependency management
- **Maintainability** - Documentation and code clarity
- **Tech Debt Index** - (lower is better) Accumulated issues

## Installation

```bash
# The archaeology module is part of src/
# It requires Python 3.8+
python -m pip install -e .
```

## Dependencies

- Python 3.8+
- `ast` (standard library) - Code parsing
- `subprocess` (standard library) - Git history analysis
- No external dependencies for core functionality

## Use Cases

1. **Legacy Code Assessment** - Understand what you're working with
2. **Architecture Reviews** - Get a second opinion on design decisions
3. **Onboarding** - Quickly understand a new codebase
4. **Modernization Planning** - Prioritize what to refactor
5. **Technical Debt Tracking** - Monitor improvements over time
6. **Team Communication** - Generate shareable analysis reports

## How It Works

1. **Initialization** - Scans repository structure
2. **Parallel Analysis**
   - Code Analyzer parses all modules
   - Historian reconstructs evolution from git
   - Debt Assessor identifies issues
3. **Validation** - Cross-checks findings against evidence
4. **Synthesis** - Generates recommendations based on findings
5. **Reporting** - Creates actionable reports

## Performance

Analysis times depend on codebase size:
- 5K LOC: ~2-5 seconds
- 25K LOC: ~5-15 seconds
- 100K+ LOC: ~30-60 seconds

Git history analysis is optional and can be skipped for non-git repositories.

## Confidence Scoring

Each finding includes a confidence score (0-1):
- **HIGH (0.8+)** - Strong evidence from multiple sources
- **MEDIUM (0.5-0.8)** - Good evidence but some assumptions
- **LOW (<0.5)** - Heuristic-based detection

## Future Enhancements

- [ ] Interactive CLI explorer
- [ ] Dependency graph visualization
- [ ] Trend analysis over time
- [ ] Custom rule definitions
- [ ] Machine learning-based pattern detection
- [ ] Integration with IDE plugins
- [ ] Quantified refactoring ROI estimates

## Example Report

See `.archaeology_reports/` directory after running analysis for example reports in markdown and JSON formats.

## Contributing

Contributions welcome! Areas for improvement:
- Additional pattern detection heuristics
- Better confidence scoring
- Performance optimizations
- Extended language support (currently Python)
- Domain-specific analysis modes

## License

Part of the sri-claude project.
