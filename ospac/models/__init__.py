"""Data models for OSPAC."""

from ospac.models.license import License
from ospac.models.policy import Policy
from ospac.models.compliance import ComplianceResult, PolicyResult

__all__ = [
    "License",
    "Policy",
    "ComplianceResult",
    "PolicyResult",
]