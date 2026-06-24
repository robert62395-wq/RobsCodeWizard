"""Parse error collection (v0.5.3.1)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class ParseError:
    line_number: int      # 1-based line in the source file
    snippet: str          # raw line content (truncated to 120 chars)
    reason: str           # human-readable error
    
    def __str__(self):
        return f"Line {self.line_number}: {self.reason}  --  '{self.snippet[:80]}'"


@dataclass
class ParseResult:
    rows: List[dict] = field(default_factory=list)
    errors: List[ParseError] = field(default_factory=list)
    total_lines: int = 0
    
    @property
    def has_errors(self):
        return bool(self.errors)
    
    @property
    def error_count(self):
        return len(self.errors)
    
    def summary(self):
        if not self.errors:
            return f"Parsed {len(self.rows)} rows successfully."
        return (
            f"Parsed {len(self.rows)} of {self.total_lines} rows. "
            f"{len(self.errors)} rows skipped due to errors."
        )