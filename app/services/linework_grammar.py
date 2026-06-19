"""Linework grammar tables."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LineworkGrammar:
    name: str
    begin_line: str
    end_line: str
    close_shape: Optional[str] = None
    begin_curve: Optional[str] = None
    end_curve: Optional[str] = None
    compound_curve: Optional[str] = None
    reverse_curve: Optional[str] = None
    curve_toggle: Optional[str] = None

    @property
    def all_commands(self) -> frozenset:
        return frozenset(c for c in (
            self.begin_line, self.end_line, self.close_shape,
            self.begin_curve, self.end_curve,
            self.compound_curve, self.reverse_curve, self.curve_toggle,
        ) if c is not None)

    def is_command(self, token: str) -> bool:
        if not token:
            return False
        return token.upper() in {c.upper() for c in self.all_commands}

    def is_begin(self, token: str) -> bool:
        if not token:
            return False
        t = token.upper()
        if self.begin_line and t == self.begin_line.upper():
            return True
        if self.begin_curve and t == self.begin_curve.upper():
            return True
        return False

    def is_end(self, token: str) -> bool:
        if not token:
            return False
        t = token.upper()
        if self.end_line and t == self.end_line.upper():
            return True
        if self.end_curve and t == self.end_curve.upper():
            return True
        return False


VDT_GRAMMAR = LineworkGrammar(
    name="vdt",
    begin_line="B",
    end_line="E",
    begin_curve="BC",
    end_curve="EC",
    compound_curve="CC",
    reverse_curve="RC",
    close_shape="CLS",
)

ODOT_GRAMMAR = LineworkGrammar(
    name="odot",
    begin_line="BL*",
    end_line="EL*",
    close_shape="CL*",
    curve_toggle="OC*",
)

GRAMMARS = {"vdt": VDT_GRAMMAR, "odot": ODOT_GRAMMAR}
