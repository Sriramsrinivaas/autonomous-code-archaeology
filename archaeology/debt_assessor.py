"""
Technical debt assessment - identifies code quality issues.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Optional
from collections import defaultdict

from .models import DebtItem, DebtType


class DebtAssessor:
    """Identifies technical debt in the codebase."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.debt_items: list[DebtItem] = []

    def assess(self) -> list[DebtItem]:
        """Run full debt assessment."""
        self.debt_items = []
        
        # Scan for different types of debt
        self._check_outdated_dependencies()
        self._check_dead_code()
        self._check_code_duplication()
        self._check_legacy_patterns()
        self._check_modularity()
        
        return self.debt_items

    def _check_outdated_dependencies(self):
        """Scan for outdated dependencies."""
        # Check requirements.txt, setup.py, pyproject.toml
        req_files = [
            self.root_path / 'requirements.txt',
            self.root_path / 'setup.py',
            self.root_path / 'pyproject.toml',
        ]
        
        for req_file in req_files:
            if not req_file.exists():
                continue
            
            try:
                content = req_file.read_text()
                
                # Simple heuristic: look for old-style dependencies
                outdated_patterns = {
                    'django==1.': 'Django 1.x is deprecated',
                    'flask==0.': 'Flask 0.x is very old',
                    'requests==2.1': 'requests 2.1.x is outdated',
                    'numpy==1.14': 'numpy 1.14.x is old',
                    'python==2.': 'Python 2 is end-of-life',
                }
                
                for pattern, reason in outdated_patterns.items():
                    if pattern in content.lower():
                        self.debt_items.append(DebtItem(
                            id=f'outdated_dep_{req_file.name}',
                            type=DebtType.OUTDATED_DEPENDENCY,
                            location=str(req_file.relative_to(self.root_path)),
                            description=f'Found {pattern}: {reason}',
                            severity='high',
                            confidence=0.8,
                            evidence=[pattern]
                        ))
            except (UnicodeDecodeError, IOError):
                pass

    def _check_dead_code(self):
        """Scan for potentially dead code."""
        python_files = list(self.root_path.rglob('*.py'))
        
        # Track all defined names
        defined = defaultdict(list)
        used = defaultdict(list)
        
        # First pass: collect definitions
        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            
            try:
                tree = ast.parse(file_path.read_text('utf-8'))
                module_name = self._get_module_name(file_path)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not node.name.startswith('_'):
                            defined[(module_name, node.name)].append(str(file_path))
            except (SyntaxError, UnicodeDecodeError):
                pass
        
        # Second pass: collect usages
        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            
            try:
                tree = ast.parse(file_path.read_text('utf-8'))
                module_name = self._get_module_name(file_path)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        used[(module_name, node.id)].append(str(file_path))
            except (SyntaxError, UnicodeDecodeError):
                pass
        
        # Find definitions with no usage
        for (module, name), locations in defined.items():
            if (module, name) not in used and len(used.get((module, name), [])) == 0:
                self.debt_items.append(DebtItem(
                    id=f'dead_code_{module}_{name}',
                    type=DebtType.DEAD_CODE,
                    location=f'{module}.{name}',
                    description=f'Function/class {name} appears unused',
                    severity='low',
                    confidence=0.5,
                    evidence=locations
                ))

    def _check_code_duplication(self):
        """Scan for duplicated code blocks."""
        python_files = list(self.root_path.rglob('*.py'))
        code_blocks = defaultdict(list)
        
        # Extract function bodies as hashes
        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            
            try:
                tree = ast.parse(file_path.read_text('utf-8'))
                module_name = self._get_module_name(file_path)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        # Simple hash of the code
                        code_hash = hash(ast.dump(node)) % (10 ** 8)
                        code_blocks[code_hash].append({
                            'module': module_name,
                            'name': node.name,
                            'file': str(file_path.relative_to(self.root_path))
                        })
            except (SyntaxError, UnicodeDecodeError):
                pass
        
        # Flag duplicates
        for code_hash, occurrences in code_blocks.items():
            if len(occurrences) > 1:
                names = ', '.join(o['name'] for o in occurrences)
                locations = [o['file'] for o in occurrences]
                
                self.debt_items.append(DebtItem(
                    id=f'duplication_{code_hash}',
                    type=DebtType.DUPLICATION,
                    location=', '.join(set(locations)),
                    description=f'Duplicated code pattern found in: {names}',
                    severity='medium',
                    confidence=0.6,
                    evidence=locations,
                    remediation_effort='medium'
                ))

    def _check_legacy_patterns(self):
        """Scan for legacy/outdated patterns."""
        python_files = list(self.root_path.rglob('*.py'))
        
        legacy_patterns = {
            'except:': 'Bare except clause (catches all exceptions)',
            'exec(': 'Use of exec() is dangerous',
            '== True': 'Comparison to True (use if x:)',
            '== False': 'Comparison to False (use if not x:)',
            'lambda:': 'Heavy lambda usage (consider def)',
            'import *': 'Wildcard imports (reduces clarity)',
        }
        
        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            
            try:
                content = file_path.read_text('utf-8')
                rel_path = str(file_path.relative_to(self.root_path))
                
                for pattern, description in legacy_patterns.items():
                    if pattern in content:
                        count = content.count(pattern)
                        self.debt_items.append(DebtItem(
                            id=f'legacy_{file_path.name}_{pattern.replace(" ", "_")}',
                            type=DebtType.LEGACY_PATTERN,
                            location=rel_path,
                            description=f'{description} (found {count} occurrences)',
                            severity='low' if count < 3 else 'medium',
                            confidence=0.7,
                            evidence=[pattern]
                        ))
            except UnicodeDecodeError:
                pass

    def _check_modularity(self):
        """Assess modularity and identify violations."""
        python_files = list(self.root_path.rglob('*.py'))
        
        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            
            try:
                content = file_path.read_text('utf-8')
                tree = ast.parse(content)
                lines = content.split('\n')
                
                # Check file size (over 500 lines is a smell)
                if len(lines) > 500:
                    self.debt_items.append(DebtItem(
                        id=f'modularity_{file_path.name}',
                        type=DebtType.POOR_MODULARITY,
                        location=str(file_path.relative_to(self.root_path)),
                        description=f'Large module ({len(lines)} lines) - consider splitting',
                        severity='medium',
                        remediation_effort='high',
                        confidence=0.8,
                        evidence=[f'{len(lines)} lines']
                    ))
                
                # Check for circular complexity (rough)
                max_complexity = 0
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._estimate_function_complexity(node)
                        max_complexity = max(max_complexity, complexity)
                
                if max_complexity > 10:
                    self.debt_items.append(DebtItem(
                        id=f'complexity_{file_path.name}',
                        type=DebtType.POOR_MODULARITY,
                        location=str(file_path.relative_to(self.root_path)),
                        description=f'High cyclomatic complexity (max: {max_complexity})',
                        severity='medium',
                        confidence=0.6,
                        evidence=[f'Complexity: {max_complexity}']
                    ))
            except (SyntaxError, UnicodeDecodeError):
                pass

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = {'__pycache__', '.venv', 'venv', '.git', 'node_modules', 'dist', 'build'}
        return any(pattern in file_path.parts for pattern in skip_patterns)

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        relative = file_path.relative_to(self.root_path)
        return str(relative.with_suffix('')).replace('\\', '/').replace('/', '.')

    def _estimate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Estimate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
