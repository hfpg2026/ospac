"""
OSPAC - Open Source Policy as Code

A comprehensive policy engine for automated OSS license compliance.
"""

__version__ = "0.1.0"

from ospac.runtime.engine import PolicyRuntime
from ospac.models.license import License
from ospac.models.policy import Policy
from ospac.models.compliance import ComplianceResult

__all__ = [
    "PolicyRuntime",
    "License",
    "Policy",
    "ComplianceResult",
]