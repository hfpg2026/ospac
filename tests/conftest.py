"""
Pytest configuration and fixtures for OSPAC tests.
"""

import pytest
from pathlib import Path
import tempfile
import yaml
import json


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_policy_yaml(temp_dir):
    """Create a sample policy YAML file."""
    policy = {
        "version": "1.0",
        "name": "Test Policy",
        "rules": [
            {
                "id": "test_rule",
                "description": "Test rule",
                "when": {"license_type": "copyleft_strong"},
                "then": {
                    "action": "deny",
                    "severity": "error",
                    "message": "Test message"
                }
            }
        ]
    }

    policy_file = temp_dir / "test_policy.yaml"
    with open(policy_file, "w") as f:
        yaml.dump(policy, f)

    return policy_file


@pytest.fixture
def sample_license_yaml(temp_dir):
    """Create a sample license YAML file."""
    license_data = {
        "license": {
            "id": "MIT",
            "name": "MIT License",
            "type": "permissive",
            "spdx_id": "MIT",
            "properties": {
                "commercial_use": True,
                "distribution": True,
                "modification": True,
                "private_use": True
            },
            "requirements": {
                "include_license": True,
                "include_copyright": True
            },
            "compatibility": {
                "static_linking": {
                    "compatible_with": ["category:any"]
                }
            }
        }
    }

    license_file = temp_dir / "MIT.yaml"
    with open(license_file, "w") as f:
        yaml.dump(license_data, f)

    return license_file


@pytest.fixture
def policy_directory(temp_dir):
    """Create a directory with multiple policy files."""
    policies_dir = temp_dir / "policies"
    policies_dir.mkdir()

    # Create license policy
    licenses_dir = policies_dir / "licenses" / "spdx"
    licenses_dir.mkdir(parents=True)

    mit_license = {
        "license": {
            "id": "MIT",
            "type": "permissive",
            "requirements": {
                "include_license": True,
                "include_copyright": True
            }
        }
    }

    gpl_license = {
        "license": {
            "id": "GPL-3.0",
            "type": "copyleft_strong",
            "requirements": {
                "disclose_source": True,
                "same_license": True
            }
        }
    }

    with open(licenses_dir / "MIT.yaml", "w") as f:
        yaml.dump(mit_license, f)

    with open(licenses_dir / "GPL-3.0.yaml", "w") as f:
        yaml.dump(gpl_license, f)

    # Create compatibility rules
    compat_dir = policies_dir / "compatibility"
    compat_dir.mkdir()

    compat_rules = {
        "version": "1.0",
        "rules": [
            {
                "id": "copyleft_contamination",
                "when": {
                    "license_type": "copyleft_strong",
                    "link_type": "static"
                },
                "then": {
                    "action": "contaminate",
                    "severity": "error"
                }
            }
        ]
    }

    with open(compat_dir / "rules.yaml", "w") as f:
        yaml.dump(compat_rules, f)

    return policies_dir


@pytest.fixture
def mock_spdx_data():
    """Mock SPDX license data."""
    return {
        "licenses": [
            {
                "licenseId": "MIT",
                "name": "MIT License",
                "isOsiApproved": True,
                "isFsfLibre": True,
                "isDeprecatedLicenseId": False,
                "detailsUrl": "https://spdx.org/licenses/MIT.json",
                "reference": "https://spdx.org/licenses/MIT.html",
                "seeAlso": ["https://opensource.org/licenses/MIT"]
            },
            {
                "licenseId": "Apache-2.0",
                "name": "Apache License 2.0",
                "isOsiApproved": True,
                "isFsfLibre": True,
                "isDeprecatedLicenseId": False,
                "detailsUrl": "https://spdx.org/licenses/Apache-2.0.json",
                "reference": "https://spdx.org/licenses/Apache-2.0.html",
                "seeAlso": ["https://www.apache.org/licenses/LICENSE-2.0"]
            },
            {
                "licenseId": "GPL-3.0",
                "name": "GNU General Public License v3.0",
                "isOsiApproved": True,
                "isFsfLibre": True,
                "isDeprecatedLicenseId": False,
                "detailsUrl": "https://spdx.org/licenses/GPL-3.0.json",
                "reference": "https://spdx.org/licenses/GPL-3.0.html",
                "seeAlso": ["https://www.gnu.org/licenses/gpl-3.0.html"]
            }
        ],
        "licenseListVersion": "3.22",
        "releaseDate": "2024-01-01"
    }


@pytest.fixture
def generated_database(temp_dir):
    """Create a mock generated database."""
    database = {
        "version": "1.0",
        "licenses": {
            "MIT": {
                "id": "MIT",
                "name": "MIT License",
                "category": "permissive",
                "permissions": {
                    "commercial_use": True,
                    "distribution": True,
                    "modification": True
                },
                "conditions": {
                    "include_license": True,
                    "include_copyright": True
                },
                "obligations": [
                    "Include license text",
                    "Include copyright notice"
                ]
            },
            "GPL-3.0": {
                "id": "GPL-3.0",
                "name": "GNU General Public License v3.0",
                "category": "copyleft_strong",
                "permissions": {
                    "commercial_use": True,
                    "distribution": True,
                    "modification": True
                },
                "conditions": {
                    "disclose_source": True,
                    "same_license": True,
                    "include_license": True
                },
                "obligations": [
                    "Disclose source code",
                    "Use same license",
                    "Include license text"
                ]
            }
        }
    }

    db_file = temp_dir / "ospac_license_database.json"
    with open(db_file, "w") as f:
        json.dump(database, f)

    return db_file