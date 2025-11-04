"""
Rule evaluation engine.
"""

from typing import Dict, Any, List, Optional


class RuleEvaluator:
    """Evaluate rules against context."""

    def __init__(self, policies: Dict[str, Any]):
        """Initialize with loaded policies."""
        self.policies = policies

    def evaluate_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single rule against the context."""
        result = {
            "rule_id": rule.get("id", "unknown"),
            "description": rule.get("description", ""),
            "matched": True,
            "action": None,
            "severity": None,
            "message": None,
        }

        # Execute the "then" clause
        if "then" in rule:
            then_clause = rule["then"]
            result["action"] = then_clause.get("action", "allow")
            result["severity"] = then_clause.get("severity", "info")

            # Format message with context
            if "message" in then_clause:
                message = then_clause["message"]
                try:
                    result["message"] = message.format(**context)
                except KeyError:
                    result["message"] = message

            # Add requirements if any
            if "requirements" in then_clause:
                result["requirements"] = then_clause["requirements"]

            # Add remediation if specified
            if "remediation" in then_clause:
                result["remediation"] = then_clause["remediation"]

        return result

    def evaluate_decision_tree(self, tree: List[Dict], context: Dict[str, Any]) -> Optional[Dict]:
        """Evaluate a decision tree against context."""
        for node in tree:
            if self._matches_condition(node.get("if", {}), context):
                return node.get("then", {})

        return None

    def _matches_condition(self, condition: Dict, context: Dict) -> bool:
        """Check if a condition matches the context."""
        for key, expected_value in condition.items():
            actual_value = context.get(key)

            if actual_value is None:
                return False

            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            elif actual_value != expected_value:
                return False

        return True