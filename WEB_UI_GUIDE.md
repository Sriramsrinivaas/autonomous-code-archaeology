# Web UI Setup Guide

## Overview

The Autonomous Code Archaeology Agent now includes a **Streamlit-based web interface** for interactive code analysis.

## Features

✨ **Interactive Web UI**
- 🔍 Repository analysis with real-time progress
- 📊 Quality score dashboard
- 🏗️ Architectural decision explorer
- 🚨 Technical debt browser
- 💡 Recommendation viewer
- 📄 Report generation and download

## Installation

### 1. Install UI Dependencies

```bash
pip install -r requirements-ui.txt
```

Or install everything:
```bash
pip install streamlit>=1.28.0
```

### 2. Run the Web UI

```bash
streamlit run app.py
```

This will:
- Open a browser window to `http://localhost:8501`
- Start the Streamlit development server
- Display the Code Archaeology web interface

## Usage

### Analyze a Repository

1. **Enter Repository Path**
   - In the left sidebar, enter the path to your repository
   - Default: `.` (current directory)

2. **Configure Options**
   - Toggle "Include Git History" for architectural evolution analysis
   - Choose report format (Markdown, JSON, or both)

3. **Click "Analyze Repository"**
   - Watch progress as agents run
   - Wait for completion (~1-2 minutes for large repos)

4. **View Results**
   - Browse multiple tabs:
     - **Summary** - Code structure overview
     - **Architecture** - Architectural decisions with evidence
     - **Tech Debt** - Issues by severity
     - **Recommendations** - Prioritized improvements
     - **Reports** - Download full analysis reports

### Interact with Findings

- **Expand sections** to see detailed information
- **Filter debt items** by severity
- **Download reports** in Markdown or JSON
- **View previews** of full reports

## Interface Overview

### Left Sidebar
- 🏠 Configuration panel
- 📝 Repository path input
- ⚙️ Analysis options
- 🚀 Analyze button

### Main Content
- 📊 Quality score cards (Architecture, Modularity, Maintainability, Tech Debt)
- 5 Result tabs with detailed findings
- 📄 Report download buttons

## Performance

| Repository Size | Analysis + UI Time |
|-----------------|-------------------|
| 5K LOC          | 3-4 seconds       |
| 25K LOC         | 5-8 seconds       |
| 100K+ LOC       | 45-90 seconds     |

## Features by Tab

### 📋 Summary
- Total modules, classes, functions
- Design patterns identified
- Quick overview of codebase structure

### 🏗️ Architecture
- Architectural decisions extracted
- Confidence scores for each decision
- Evidence and rationale
- Impact assessment

### 🚨 Tech Debt
- Debt items filtered by severity (high/medium/low)
- Type categorization
- Confidence scores
- Remediation effort estimates

### 💡 Recommendations
- Prioritized suggestions (high/medium)
- Quick wins highlighted with ⚡
- Implementation steps
- Risk assessment
- Related debt items

### 📄 Reports
- Download full Markdown report
- Download JSON export
- View report preview

## Customization

### Colors & Styling
Edit the CSS in `app.py` under "Custom CSS" section to change:
- Color schemes
- Card styling
- Font sizes

### Layout Options
Current layout is `wide`. To change:
```python
st.set_page_config(layout="centered")  # or "wide"
```

### Tabs & Sections
Add or remove tabs by modifying the tabs section in `main()` function.

## Troubleshooting

### "Module not found" Error
```bash
# Make sure archaeology module is in path
cd autonomous-code-archaeology
streamlit run app.py
```

### Slow Analysis
- Large repositories (100K+ LOC) may take 1-2 minutes
- Git history analysis adds ~20-30% overhead
- Uncheck "Include Git History" for faster analysis

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

## Advanced Usage

### Analyze Remote Repository
```bash
# Clone repo first
git clone https://github.com/user/repo.git
streamlit run app.py
# Enter path: ./repo
```

### Batch Analysis
```python
# Create a script to analyze multiple repos
from pathlib import Path

repos = ["/path/repo1", "/path/repo2", "/path/repo3"]
for repo in repos:
    orchestrator = ArchaeologyOrchestrator(repo)
    result = orchestrator.run_analysis()
    ReportGenerator.save_report(result, Path("./reports"))
```

### API Integration
The Streamlit app uses the same Python API as CLI:
```python
from archaeology import ArchaeologyOrchestrator

orchestrator = ArchaeologyOrchestrator("/path/to/repo")
result = orchestrator.run_analysis()

# Access results programmatically
print(result.architecture_quality_score)
print(len(result.tech_debt_items))
```

## Future Enhancements

- [ ] Multi-repository comparison
- [ ] Historical trend graphs
- [ ] Team collaboration features
- [ ] Custom rule configuration UI
- [ ] Export to PDF
- [ ] Dark mode theme
- [ ] API endpoints for external integration

## Requirements

- Python 3.8+
- Streamlit 1.28.0+
- archaeology module (this package)

## Support

For issues or questions:
1. Check the main [README.md](../README.md)
2. Review [docs/](../docs/) directory
3. Open an issue on GitHub

---

**Happy Analyzing!** 🔍
