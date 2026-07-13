"""Rule-based checks of an agent against a machine-readable YAML policy.

Compares an agent's declared autonomy, action space, and data reach against the limits in a policy
file (see ``policies/example-policy.yaml``) and reports violations. Landed in milestone M6.
"""

from __future__ import annotations
