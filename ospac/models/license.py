"""
License data model.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class License:
    """Represents a software license with its properties and requirements."""

    id: str
    name: str
    type: str  # permissive, copyleft_weak, copyleft_strong, proprietary
    spdx_id: Optional[str] = None

    properties: Dict[str, bool] = field(default_factory=dict)
    requirements: Dict[str, bool] = field(default_factory=dict)
    compatibility: Dict[str, Dict] = field(default_factory=dict)

    def is_compatible_with(self, other: "License", context: str = "general") -> bool:
        """Check if this license is compatible with another."""
        if context not in self.compatibility:
            context = "general"

        if context in self.compatibility:
            compat_rules = self.compatibility[context]

            # Check explicit compatible list
            if "compatible_with" in compat_rules:
                if other.id in compat_rules["compatible_with"]:
                    return True
                if other.type in compat_rules["compatible_with"]:
                    return True

            # Check explicit incompatible list
            if "incompatible_with" in compat_rules:
                if other.id in compat_rules["incompatible_with"]:
                    return False
                if other.type in compat_rules["incompatible_with"]:
                    return False

        # Default: permissive licenses are generally compatible
        if self.type == "permissive" and other.type == "permissive":
            return True

        return False

    def get_obligations(self) -> List[str]:
        """Get all obligations for this license."""
        obligations = []

        if self.requirements.get("disclose_source"):
            obligations.append("Disclose source code")

        if self.requirements.get("include_license"):
            obligations.append("Include license text")

        if self.requirements.get("include_copyright"):
            obligations.append("Include copyright notice")

        if self.requirements.get("state_changes"):
            obligations.append("State changes made to the code")

        if self.requirements.get("same_license"):
            obligations.append("Distribute under same license")

        return obligations

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "License":
        """Create a License instance from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            spdx_id=data.get("spdx_id"),
            properties=data.get("properties", {}),
            requirements=data.get("requirements", {}),
            compatibility=data.get("compatibility", {}),
        )