"""
Code Archaeology Agent System

Autonomous multi-agent system for analyzing code repositories to understand
architectural decisions, identify tech debt, and propose modernization strategies.
"""

from .models import (
    CodeGraph,
    Module,
    ClassDef,
    FunctionDef,
    ArchitecturalDecision,
    DebtItem,
    Recommendation,
    AnalysisResult,
    DebtType,
    PatternType,
)
from .orchestrator import ArchaeologyOrchestrator
from .analyzer import CodeAnalyzer
from .historian import HistoryAnalyzer
from .debt_assessor import DebtAssessor
from .reporter import ReportGenerator

__all__ = [
    'ArchaeologyOrchestrator',
    'CodeAnalyzer',
    'HistoryAnalyzer',
    'DebtAssessor',
    'ReportGenerator',
    'CodeGraph',
    'Module',
    'ClassDef',
    'FunctionDef',
    'ArchitecturalDecision',
    'DebtItem',
    'Recommendation',
    'AnalysisResult',
    'DebtType',
    'PatternType',
]
