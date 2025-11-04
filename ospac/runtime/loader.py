"""
Policy file loader.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List


class PolicyLoader:
    """Load and parse policy definitions from files."""

    SUPPORTED_EXTENSIONS = {".yaml", ".yml", ".json"}

    def load_all(self, policy_path: str) -> Dict[str, Any]:
        """Load all policy files from the specified directory."""
        path = Path(policy_path)
        if not path.exists():
            raise FileNotFoundError(f"Policy path not found: {policy_path}")

        policies = {}

        if path.is_file():
            name = path.stem
            policies[name] = self.load_file(str(path))
        else:
            for file_path in path.rglob("*"):
                if file_path.suffix in self.SUPPORTED_EXTENSIONS:
                    relative_name = file_path.relative_to(path).with_suffix("")
                    policies[str(relative_name)] = self.load_file(str(file_path))

        return policies

    def load_file(self, file_path: str) -> Dict[str, Any]:
        """Load a single policy file."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            if path.suffix == ".json":
                return json.load(f)
            elif path.suffix in {".yaml", ".yml"}:
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")

    def validate_policy(self, policy: Dict[str, Any]) -> bool:
        """Validate a policy against the schema."""
        # TODO: Implement schema validation using jsonschema
        required_fields = {"version", "rules"}
        return all(field in policy for field in required_fields)