"""
Code structure analysis - extracts modules, classes, functions, and patterns.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from .models import (
    CodeGraph,
    Module,
    ClassDef,
    FunctionDef,
    PatternType,
    ArchitecturalDecision,
)


class CodeAnalyzer:
    """Analyzes Python code structure and extracts architectural information."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.graph = CodeGraph(root_path=root_path)

    def analyze(self) -> CodeGraph:
        """Analyze entire codebase and build dependency graph."""
        # Find all Python files
        python_files = list(self.root_path.rglob('*.py'))
        
        # Parse each file
        for file_path in python_files:
            if self._should_skip(file_path):
                continue
            self._analyze_file(file_path)
        
        # Build import graph
        self._build_import_graph()
        self._detect_circular_dependencies()
        
        return self.graph

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = {'__pycache__', '.venv', 'venv', '.git', 'node_modules', 'dist', 'build'}
        return any(pattern in file_path.parts for pattern in skip_patterns)

    def _analyze_file(self, file_path: Path) -> Optional[Module]:
        """Analyze a single Python file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            module_name = self._get_module_name(file_path)
            module = Module(
                path=str(file_path.relative_to(self.root_path)),
                name=module_name,
                size=len(content),
                docstring=ast.get_docstring(tree),
            )
            
            # Extract imports
            imports = self._extract_imports(tree)
            module.imports = imports
            
            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_def = self._analyze_class(node, module_name)
                    if class_def:
                        module.classes[class_def.name] = class_def
                
                elif isinstance(node, ast.FunctionDef):
                    # Skip methods (they're handled in classes)
                    if not any(isinstance(p, ast.ClassDef) for p in ast.walk(tree)):
                        func_def = self._analyze_function(node, module_name)
                        if func_def:
                            module.functions[func_def.name] = func_def
            
            # Estimate test coverage
            module.test_coverage = self._estimate_test_coverage(file_path)
            
            self.graph.modules[module_name] = module
            return module
            
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return None

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        relative = file_path.relative_to(self.root_path)
        return str(relative.with_suffix('')).replace('\\', '/').replace('/', '.')

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """Extract all imports from module."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return list(set(imports))

    def _analyze_class(self, node: ast.ClassDef, module_name: str) -> Optional[ClassDef]:
        """Analyze a class definition."""
        class_def = ClassDef(
            name=node.name,
            module=module_name,
            bases=[self._get_name(base) for base in node.bases],
            docstring=ast.get_docstring(node),
            is_public=not node.name.startswith('_'),
        )
        
        # Count lines
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            class_def.line_count = node.end_lineno - node.lineno
        
        # Extract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method = self._analyze_function(item, module_name, class_name=node.name)
                if method:
                    class_def.methods[method.name] = method

        return class_def

    def _analyze_function(
        self, node: ast.FunctionDef, module_name: str, class_name: Optional[str] = None
    ) -> Optional[FunctionDef]:
        """Analyze a function definition."""
        func_def = FunctionDef(
            name=node.name,
            module=module_name,
            class_name=class_name,
            params=[arg.arg for arg in node.args.args],
            docstring=ast.get_docstring(node),
            is_public=not node.name.startswith('_'),
        )
        
        # Extract return type annotation
        if node.returns:
            func_def.return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else None
        
        # Count lines
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            func_def.line_count = node.end_lineno - node.lineno
        
        # Estimate cyclomatic complexity
        func_def.cyclomatic_complexity = self._estimate_complexity(node)
        
        # Extract calls
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    func_def.calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    func_def.calls.append(child.func.attr)
        
        return func_def

    def _estimate_complexity(self, node: ast.AST) -> int:
        """Rough estimate of cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        return complexity

    def _get_name(self, node: ast.expr) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif hasattr(ast, 'unparse'):
            return ast.unparse(node)
        return 'Unknown'

    def _build_import_graph(self):
        """Build module dependency graph."""
        for module_name, module in self.graph.modules.items():
            for imported in module.imports:
                if imported not in self.graph.all_imports:
                    self.graph.all_imports[imported] = set()
                self.graph.all_imports[imported].add(module_name)
                
                # Check if it's an external dependency
                if not any(imp.startswith(imported) for imp in self.graph.modules.keys()):
                    self.graph.external_dependencies.add(imported)

    def _detect_circular_dependencies(self):
        """Detect circular import dependencies."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(module: str, path: set[str]) -> bool:
            visited.add(module)
            path.add(module)
            
            module_obj = self.graph.modules.get(module)
            if module_obj is None:
                # Create a placeholder module for external imports
                module_obj = Module(path='', name=module, size=0)
            imports = module_obj.imports
            
            for imported in imports:
                if imported not in visited:
                    if has_cycle(imported, path):
                        return True
                elif imported in path:
                    self.graph.circular_dependencies.append((module, imported))
                    return True
            
            path.remove(module)
            return False
        
        for module_name in self.graph.modules:
            if module_name not in visited:
                has_cycle(module_name, set())

    def _estimate_test_coverage(self, file_path: Path) -> float:
        """Estimate test coverage for a module."""
        # Simple heuristic: check if there's a test file
        test_variants = [
            file_path.parent / f'test_{file_path.name}',
            file_path.parent / f'{file_path.stem}_test.py',
            file_path.parent / 'tests' / file_path.name,
        ]
        
        for test_file in test_variants:
            if test_file.exists():
                return 0.7  # Assume decent coverage if test file exists
        
        return 0.0

    def extract_patterns(self) -> list[str]:
        """Identify design patterns used in codebase."""
        patterns = []
        
        for module in self.graph.modules.values():
            for class_def in module.classes.values():
                # Detection heuristics
                if self._is_singleton(class_def):
                    patterns.append(f"{PatternType.SINGLETON.value}:{class_def.name}")
                if self._is_factory(class_def):
                    patterns.append(f"{PatternType.FACTORY.value}:{class_def.name}")
                if self._is_strategy(class_def):
                    patterns.append(f"{PatternType.STRATEGY.value}:{class_def.name}")
        
        return patterns

    def _is_singleton(self, class_def: ClassDef) -> bool:
        """Heuristic: check if class looks like a singleton."""
        # Look for __instance or _instance
        if any('instance' in method.lower() for method in class_def.methods.keys()):
            return True
        return False

    def _is_factory(self, class_def: ClassDef) -> bool:
        """Heuristic: check if class looks like a factory."""
        # Look for 'create', 'make', 'build' methods
        creation_keywords = {'create', 'make', 'build', 'from', 'construct'}
        return any(
            method_name.lower().split('_')[0] in creation_keywords
            for method_name in class_def.methods.keys()
        )

    def _is_strategy(self, class_def: ClassDef) -> bool:
        """Heuristic: check if class looks like a strategy."""
        # Look for 'execute', 'run', 'process' method
        return any(
            method_name in {'execute', 'run', 'process', 'apply'}
            for method_name in class_def.methods.keys()
        )
