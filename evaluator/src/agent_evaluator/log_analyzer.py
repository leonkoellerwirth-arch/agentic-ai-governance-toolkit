"""Flags an agent's runtime logs against operational thresholds.

Reads a JSONL audit trail and reports where escalation rate, error rate, or blocked-action counts
cross the thresholds a policy defines. Landed in milestone M6.
"""

from __future__ import annotations
