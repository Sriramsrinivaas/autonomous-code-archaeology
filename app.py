"""
Streamlit web UI for Autonomous Code Archaeology Agent
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime

# Import the archaeology module
import sys
sys.path.insert(0, str(Path(__file__).parent))

from archaeology import ArchaeologyOrchestrator
from archaeology.reporter import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="Code Archaeology",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .score-100 { color: #28a745; font-weight: bold; }
    .score-75 { color: #ffc107; font-weight: bold; }
    .score-50 { color: #fd7e14; font-weight: bold; }
    .score-25 { color: #dc3545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def score_color(score):
    """Return color class based on score"""
    if score >= 80:
        return "score-100"
    elif score >= 60:
        return "score-75"
    elif score >= 40:
        return "score-50"
    else:
        return "score-25"

def main():
    st.title("🔍 Code Archaeology Agent")
    st.markdown("Autonomous multi-agent system for analyzing code repositories")
    
    # Sidebar inputs
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        repo_path = st.text_input(
            "Repository Path",
            value=".",
            help="Local path to the repository to analyze"
        )
        
        include_history = st.checkbox(
            "Include Git History",
            value=True,
            help="Analyze git commits for architectural evolution"
        )
        
        output_format = st.radio(
            "Report Format",
            ["markdown", "json", "both"],
            help="Choose output format for the report"
        )
        
        analyze_button = st.button(
            "🚀 Analyze Repository",
            use_container_width=True,
            type="primary"
        )
    
    # Main content area
    if analyze_button:
        if not repo_path:
            st.error("Please provide a repository path")
            return
        
        repo_path_obj = Path(repo_path).resolve()
        if not repo_path_obj.exists():
            st.error(f"❌ Repository not found: {repo_path}")
            return
        
        # Run analysis with progress
        with st.spinner("🔄 Analyzing repository..."):
            try:
                orchestrator = ArchaeologyOrchestrator(str(repo_path_obj))
                result = orchestrator.run_analysis()
                
                # Store result in session state
                st.session_state.analysis_result = result
                st.session_state.show_results = True
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                return
    
    # Display results if available
    if st.session_state.get("show_results") and st.session_state.get("analysis_result"):
        result = st.session_state.analysis_result
        
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # Repository info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Repository", result.repository_name)
        with col2:
            st.metric("Analysis Time", f"{result.analysis_duration_seconds:.2f}s")
        with col3:
            st.metric("Modules", len(result.code_graph.modules) if result.code_graph else 0)
        
        # Quality scores
        st.subheader("🎯 Quality Scores")
        
        score_col1, score_col2, score_col3, score_col4 = st.columns(4)
        
        with score_col1:
            st.metric(
                "Architecture Quality",
                f"{result.architecture_quality_score:.0f}/100",
                delta=f"{result.architecture_quality_score - 50:.0f}"
            )
        
        with score_col2:
            st.metric(
                "Modularity",
                f"{result.modularity_score:.0f}/100",
                delta=f"{result.modularity_score - 50:.0f}"
            )
        
        with score_col3:
            st.metric(
                "Maintainability",
                f"{result.maintainability_score:.0f}/100",
                delta=f"{result.maintainability_score - 50:.0f}"
            )
        
        with score_col4:
            st.metric(
                "Tech Debt",
                f"{result.tech_debt_score:.0f}/100",
                delta=f"-{100 - result.tech_debt_score:.0f}",
                delta_color="inverse"
            )
        
        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Summary",
            "🏗️ Architecture",
            "🚨 Tech Debt",
            "💡 Recommendations",
            "📄 Reports"
        ])
        
        # Tab 1: Summary
        with tab1:
            st.subheader("Code Structure")
            if result.code_graph:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Modules**: {len(result.code_graph.modules)}")
                with col2:
                    total_classes = sum(len(m.classes) for m in result.code_graph.modules.values())
                    st.markdown(f"**Classes**: {total_classes}")
                with col3:
                    total_functions = sum(len(m.functions) for m in result.code_graph.modules.values())
                    st.markdown(f"**Functions**: {total_functions}")
            
            st.subheader("Design Patterns")
            if result.identified_patterns:
                pattern_cols = st.columns(2)
                for i, pattern in enumerate(result.identified_patterns[:6]):
                    with pattern_cols[i % 2]:
                        st.code(pattern, language="text")
            else:
                st.info("No common patterns detected")
        
        # Tab 2: Architectural Decisions
        with tab2:
            st.subheader("Architectural Decisions")
            if result.architectural_decisions:
                for decision in result.architectural_decisions:
                    with st.expander(f"🏛️ {decision.name} ({decision.confidence*100:.0f}% confidence)"):
                        st.markdown(f"**Description**: {decision.description}")
                        st.markdown(f"**Rationale**: {decision.rationale}")
                        st.markdown(f"**Impact**: {decision.impact}")
                        if decision.evidence:
                            st.markdown("**Evidence**:")
                            for ev in decision.evidence[:3]:
                                st.markdown(f"- {ev}")
            else:
                st.info("No architectural decisions identified")
        
        # Tab 3: Technical Debt
        with tab3:
            st.subheader("Technical Debt Items")
            if result.tech_debt_items:
                # Filter by severity
                severity_filter = st.multiselect(
                    "Filter by severity",
                    ["high", "medium", "low"],
                    default=["high", "medium"]
                )
                
                filtered_debt = [d for d in result.tech_debt_items if d.severity in severity_filter]
                
                # Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**High**: {len([d for d in filtered_debt if d.severity == 'high'])}")
                with col2:
                    st.markdown(f"**Medium**: {len([d for d in filtered_debt if d.severity == 'medium'])}")
                with col3:
                    st.markdown(f"**Low**: {len([d for d in filtered_debt if d.severity == 'low'])}")
                
                st.markdown("---")
                
                # List debt items
                for item in filtered_debt[:20]:  # Limit to 20 for performance
                    severity_icon = "🔴" if item.severity == "high" else "🟡" if item.severity == "medium" else "🟢"
                    with st.expander(f"{severity_icon} {item.type.value} in {item.location}"):
                        st.markdown(f"**Description**: {item.description}")
                        st.markdown(f"**Confidence**: {item.confidence*100:.0f}%")
                        if item.impact:
                            st.markdown(f"**Impact**: {item.impact}")
                        if item.remediation_effort:
                            st.markdown(f"**Remediation Effort**: {item.remediation_effort}")
            else:
                st.info("No technical debt items identified")
        
        # Tab 4: Recommendations
        with tab4:
            st.subheader("Modernization Recommendations")
            if result.modernization_recommendations:
                # Separate by priority
                high_pri = [r for r in result.modernization_recommendations if r.priority == "high"]
                medium_pri = [r for r in result.modernization_recommendations if r.priority == "medium"]
                
                # High priority
                if high_pri:
                    st.markdown("### 🔴 High Priority")
                    for rec in high_pri:
                        with st.expander(f"{'⚡' if rec.quick_win else '📋'} {rec.title}"):
                            st.markdown(f"**Category**: {rec.category}")
                            st.markdown(f"**Description**: {rec.description}")
                            st.markdown(f"**Rationale**: {rec.rationale}")
                            st.markdown(f"**Effort**: {rec.estimated_effort}")
                            st.markdown(f"**Confidence**: {rec.confidence*100:.0f}%")
                            if rec.quick_win:
                                st.success("⚡ Quick Win!")
                            if rec.implementation_steps:
                                st.markdown("**Steps**:")
                                for i, step in enumerate(rec.implementation_steps, 1):
                                    st.markdown(f"{i}. {step}")
                
                # Medium priority
                if medium_pri:
                    st.markdown("### 🟡 Medium Priority")
                    for rec in medium_pri[:3]:  # Show top 3
                        with st.expander(f"{rec.title}"):
                            st.markdown(f"**Description**: {rec.description}")
                            st.markdown(f"**Effort**: {rec.estimated_effort}")
            else:
                st.info("No recommendations available")
        
        # Tab 5: Reports
        with tab5:
            st.subheader("Download Reports")
            
            # Generate reports
            report_dir = Path(".archaeology_reports")
            saved = ReportGenerator.save_report(result, report_dir, formats=["md", "json"])
            
            col1, col2 = st.columns(2)
            
            # Markdown report
            if "markdown" in saved:
                with col1:
                    md_content = saved["markdown"].read_text(encoding="utf-8")
                    st.download_button(
                        label="📄 Download Markdown Report",
                        data=md_content,
                        file_name=saved["markdown"].name,
                        mime="text/markdown",
                        use_container_width=True
                    )
            
            # JSON report
            if "json" in saved:
                with col2:
                    json_content = saved["json"].read_text(encoding="utf-8")
                    st.download_button(
                        label="📋 Download JSON Report",
                        data=json_content,
                        file_name=saved["json"].name,
                        mime="application/json",
                        use_container_width=True
                    )
            
            # Display reports
            st.markdown("---")
            st.subheader("Report Preview")
            
            if "markdown" in saved:
                with st.expander("📄 Markdown Report"):
                    md_content = saved["markdown"].read_text(encoding="utf-8")
                    st.markdown(md_content[:2000] + "\n\n*... (truncated, see full report in download)*")

if __name__ == "__main__":
    # Initialize session state
    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    
    main()
