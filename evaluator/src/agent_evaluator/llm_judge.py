"""OPTIONAL evaluator-agent pattern: a local LLM judges agent outputs against a policy.

This is a demonstration of the "LLM-as-judge" control, run locally via Ollama and cleanly isolated
behind an optional dependency — the core evaluator never imports it. It is a reference pattern, not
a production system. Landed in milestone M6.
"""

from __future__ import annotations
