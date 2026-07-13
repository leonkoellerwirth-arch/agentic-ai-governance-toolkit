"""agent_evaluator — risk scoring, policy checks, and log analysis for AI-agent governance.

The public surface is intentionally small so a reviewer can read it end to end:

- `risk_score`   — implements the control-intensity rubric (single source: ``rubric.yaml``).
- `policy_check` — rule-based checks of an agent against a machine-readable YAML policy.
- `log_analyzer` — flags an agent's runtime logs against operational thresholds.
- `llm_judge`    — an OPTIONAL evaluator-agent pattern (local Ollama); a demonstration, not a
  production system.

This is a reference pattern, not a framework, and not legal advice.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
