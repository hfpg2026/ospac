"""
Policy data model.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Rule:
    """Represents a single policy rule."""

    id: str
    description: str
    when: Dict[str, Any]
    then: Dict[str, Any]
    priority: int = 0

    def matches(self, context: Dict[str, Any]) -> bool:
        """Check if this rule matches the given context."""
        for key, expected in self.when.items():
            if key not in context:
                return False

            actual = context[key]
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False

        return True


@dataclass
class Policy:
    """Represents a compliance policy."""

    name: str
    version: str
    rules: List[Rule] = field(default_factory=list)
    extends: Optional[str] = None
    decision_tree: Optional[List[Dict]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to this policy."""
        self.rules.append(rule)
        # Sort by priority
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def evaluate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate this policy against the given context."""
        results = []

        for rule in self.rules:
            if rule.matches(context):
                result = {
                    "rule_id": rule.id,
                    "description": rule.description,
                    "action": rule.then.get("action", "allow"),
                    "severity": rule.then.get("severity", "info"),
                    "message": rule.then.get("message", ""),
                }

                if "requirements" in rule.then:
                    result["requirements"] = rule.then["requirements"]

                if "remediation" in rule.then:
                    result["remediation"] = rule.then["remediation"]

                results.append(result)

        return results

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Policy":
        """Create a Policy instance from a dictionary."""
        rules = []
        for rule_data in data.get("rules", []):
            rule = Rule(
                id=rule_data["id"],
                description=rule_data.get("description", ""),
                when=rule_data.get("when", {}),
                then=rule_data.get("then", {}),
                priority=rule_data.get("priority", 0),
            )
            rules.append(rule)

        return cls(
            name=data.get("name", "unnamed"),
            version=data.get("version", "1.0"),
            rules=rules,
            extends=data.get("extends"),
            decision_tree=data.get("decision_tree"),
            metadata=data.get("metadata", {}),
        )