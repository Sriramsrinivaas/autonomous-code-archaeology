"""
Git history analysis - reconstructs architectural evolution.
"""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, NamedTuple
from dataclasses import dataclass


class BlameEntry(NamedTuple):
    """Single blame entry from git."""
    commit_hash: str
    author: str
    date: datetime
    line_number: int
    content: str


class Commit(NamedTuple):
    """Git commit."""
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: int


@dataclass
class ArchitecturalPhase:
    """Phase in architectural evolution."""
    name: str
    start_date: datetime
    end_date: Optional[datetime]
    description: str
    major_changes: list[str]


class HistoryAnalyzer:
    """Analyzes git history to understand how code evolved."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def is_git_repo(self) -> bool:
        """Check if path is a git repository."""
        return (self.repo_path / '.git').exists()

    def get_log(self, file_path: Optional[str] = None, limit: int = 100) -> list[Commit]:
        """Get git log for repository or specific file."""
        if not self.is_git_repo():
            return []

        try:
            cmd = ['git', '-C', str(self.repo_path), 'log', '--format=%H|%an|%ai|%s', f'--max-count={limit}']
            if file_path:
                cmd.append(file_path)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|', 3)
                if len(parts) >= 4:
                    try:
                        commits.append(Commit(
                            hash=parts[0][:8],
                            author=parts[1],
                            date=datetime.fromisoformat(parts[2].replace('Z', '+00:00')),
                            message=parts[3],
                            files_changed=0  # Would need separate call to get this
                        ))
                    except ValueError:
                        pass
            
            return commits
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def get_blame(self, file_path: str, start_line: Optional[int] = None, 
                  end_line: Optional[int] = None) -> list[BlameEntry]:
        """Get blame information for a file."""
        if not self.is_git_repo():
            return []

        try:
            file_full_path = self.repo_path / file_path
            if not file_full_path.exists():
                return []

            cmd = ['git', '-C', str(self.repo_path), 'blame', '-l', '--date=short', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            blame_entries = []
            for line_num, line in enumerate(result.stdout.split('\n'), 1):
                if not line.strip():
                    continue
                
                # Parse blame output
                parts = line.split('(', 1)
                if len(parts) == 2:
                    commit_hash = parts[0].strip()[:8]
                    rest = parts[1]
                    
                    # Extract author and date
                    tokens = rest.split()
                    if len(tokens) >= 2:
                        author = tokens[0]
                        try:
                            date = datetime.fromisoformat(tokens[1])
                            content = ' '.join(tokens[2:])
                            
                            blame_entries.append(BlameEntry(
                                commit_hash=commit_hash,
                                author=author,
                                date=date,
                                line_number=line_num,
                                content=content
                            ))
                        except ValueError:
                            pass
            
            return blame_entries
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def extract_timeline(self) -> list[ArchitecturalPhase]:
        """Reconstruct timeline of major architectural changes."""
        commits = self.get_log(limit=500)
        
        if not commits:
            return []

        phases = []
        current_phase = None
        phase_keywords = {
            'refactor': 'Refactoring Phase',
            'restructure': 'Architecture Restructure',
            'migrate': 'Technology Migration',
            'upgrade': 'Dependency Upgrade',
            'optimization': 'Performance Optimization',
            'feature': 'Feature Development',
        }

        for i, commit in enumerate(commits):
            keyword = self._detect_phase_keyword(commit.message)
            
            if keyword and (not current_phase or current_phase.name != phase_keywords[keyword]):
                if current_phase:
                    current_phase.end_date = commits[i].date
                    phases.append(current_phase)
                
                current_phase = ArchitecturalPhase(
                    name=phase_keywords[keyword],
                    start_date=commit.date,
                    end_date=None,
                    description=f"Phase starting with: {commit.message[:50]}",
                    major_changes=[commit.message]
                )
            elif current_phase:
                current_phase.major_changes.append(commit.message)

        if current_phase:
            phases.append(current_phase)

        return phases

    def _detect_phase_keyword(self, message: str) -> Optional[str]:
        """Detect phase keyword in commit message."""
        message_lower = message.lower()
        keywords = ['refactor', 'restructure', 'migrate', 'upgrade', 'optimization', 'feature']
        
        for keyword in keywords:
            if keyword in message_lower:
                return keyword
        
        return None

    def extract_top_contributors(self, limit: int = 5) -> list[tuple[str, int]]:
        """Get top contributors by commit count."""
        commits = self.get_log(limit=1000)
        
        author_counts = {}
        for commit in commits:
            author_counts[commit.author] = author_counts.get(commit.author, 0) + 1
        
        return sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def extract_decision_evidence(self, pattern: str) -> list[str]:
        """Find commits that mention a specific pattern/decision."""
        commits = self.get_log(limit=200)
        
        matches = []
        pattern_lower = pattern.lower()
        
        for commit in commits:
            if pattern_lower in commit.message.lower():
                matches.append(f"{commit.hash}: {commit.message}")
        
        return matches

    def estimate_churn(self) -> dict[str, int]:
        """Estimate code churn metrics."""
        try:
            # Get file change statistics
            cmd = ['git', '-C', str(self.repo_path), 'diff', '--stat', 'HEAD~30..HEAD']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            churn = {}
            for line in result.stdout.split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        filename = parts[0].strip()
                        changes = parts[1].strip().split()
                        if changes:
                            try:
                                churn[filename] = int(changes[0])
                            except ValueError:
                                pass
            
            return churn
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {}
