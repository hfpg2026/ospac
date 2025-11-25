# OSPAC User Guide

Complete guide for using OSPAC (Open Source Policy as Code) for automated OSS license compliance.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Python API](#python-api)
- [Policy Files](#policy-files)
- [Data Management](#data-management)
- [Integration Patterns](#integration-patterns)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Installation

### Basic Installation

Install the latest stable release:

```bash
pip install ospac
```

### Installation with Extras

OSPAC provides optional feature sets:

```bash
# With SEMCL.ONE integration (osslili, purl2notices, etc.)
pip install "ospac[semcl]"

# With LLM analysis capabilities
pip install "ospac[llm]"

# Full installation with all features
pip install "ospac[all]"
```

### Requirements

- Python 3.8 or higher
- pip package manager

### Verification

Verify your installation:

```bash
ospac --version
ospac data show MIT
```

## Quick Start

### Basic License Evaluation

OSPAC v1.2.0 works immediately after installation with no setup required:

```bash
# Check if a license is allowed for your use case
ospac evaluate -l "MIT" -d commercial

# Check multiple licenses
ospac evaluate -l "GPL-3.0,MIT,Apache-2.0" -d mobile
```

### License Compatibility Check

Check if two licenses can be used together:

```bash
# Basic compatibility check
ospac check GPL-3.0 MIT

# With linking context
ospac check GPL-2.0 Apache-2.0 -c static_linking
```

### Get License Obligations

Understand what you need to do to comply:

```bash
# Get obligations for specific licenses
ospac obligations -l "Apache-2.0,MIT"

# Output in JSON format
ospac obligations -l "GPL-3.0" -f json

# Output in markdown for documentation
ospac obligations -l "MIT,BSD-3-Clause" -f markdown
```

### Create Policy Files

Generate policy templates for your project type:

```bash
# Mobile app policy (blocks GPL)
ospac policy init --template mobile --output mobile_policy.yaml

# Desktop application policy
ospac policy init --template desktop --output desktop_policy.yaml

# Embedded system policy
ospac policy init --template embedded --output embedded_policy.yaml

# Web application policy
ospac policy init --template web --output web_policy.yaml

# Server/SaaS policy
ospac policy init --template server --output server_policy.yaml

# Library policy
ospac policy init --template library --output library_policy.yaml
```

## Command Reference

### `ospac evaluate`

Evaluate licenses against organizational policies.

**Syntax:**
```bash
ospac evaluate -l LICENSES -d DISTRIBUTION [OPTIONS]
```

**Arguments:**
- `-l, --licenses` - Comma-separated list of SPDX license identifiers
- `-d, --distribution` - Distribution type (mobile, desktop, web, server, embedded, library, commercial)
- `-p, --policy` - Path to custom policy file (optional)
- `-c, --context` - Usage context (static_linking, dynamic_linking, etc.)
- `-f, --format` - Output format (json, text, yaml)

**Examples:**

```bash
# Evaluate for mobile distribution
ospac evaluate -l "GPL-3.0" -d mobile

# Evaluate with custom policy
ospac evaluate -l "MIT,Apache-2.0" -d commercial -p ./my_policy.yaml

# Get JSON output for automation
ospac evaluate -l "GPL-3.0,LGPL-2.1" -d desktop -f json

# Evaluate with specific context
ospac evaluate -l "GPL-2.0,Apache-2.0" -d commercial -c static_linking
```

**Output Fields:**
- `action` - approve, deny, or review
- `severity` - info, warning, or error
- `message` - Human-readable explanation
- `requirements` - List of compliance requirements (if approved)
- `remediation` - Suggested fix (if denied)
- `obligations` - Detailed license obligations

### `ospac check`

Check compatibility between two licenses.

**Syntax:**
```bash
ospac check LICENSE1 LICENSE2 [OPTIONS]
```

**Arguments:**
- `LICENSE1` - First SPDX license identifier
- `LICENSE2` - Second SPDX license identifier
- `-c, --context` - Usage context (static_linking, dynamic_linking, general)
- `-f, --format` - Output format (json, text, yaml)

**Examples:**

```bash
# Basic compatibility check
ospac check GPL-3.0 MIT

# Check with static linking context
ospac check GPL-2.0 Apache-2.0 -c static_linking

# Check with dynamic linking (may allow more combinations)
ospac check LGPL-2.1 Apache-2.0 -c dynamic_linking

# JSON output
ospac check GPL-3.0 BSD-3-Clause -f json
```

**Output Fields:**
- `compatible` - Boolean indicating compatibility
- `reason` - Explanation of compatibility or incompatibility
- `restrictions` - Any special conditions
- `recommendations` - Suggested actions

### `ospac obligations`

Get detailed compliance obligations for licenses.

**Syntax:**
```bash
ospac obligations -l LICENSES [OPTIONS]
```

**Arguments:**
- `-l, --licenses` - Comma-separated list of SPDX license identifiers
- `-f, --format` - Output format (json, text, markdown, checklist)

**Examples:**

```bash
# Get obligations for multiple licenses
ospac obligations -l "Apache-2.0,MIT,BSD-3-Clause"

# Get as markdown for documentation
ospac obligations -l "GPL-3.0" -f markdown

# Get as checklist for compliance tracking
ospac obligations -l "Apache-2.0" -f checklist

# JSON output for automation
ospac obligations -l "MIT,ISC,0BSD" -f json
```

**Output Fields:**
- `permissions` - What you CAN do (commercial use, modification, distribution)
- `requirements` - What you MUST do (include license, preserve copyright, disclose source)
- `limitations` - What is NOT provided (liability, warranty, trademark use)
- `obligations` - Specific compliance requirements
- `conditions` - Additional conditions for compliance

### `ospac policy`

Manage policy files.

**Subcommands:**

#### `ospac policy init`

Create a new policy file from template.

```bash
# Create mobile app policy
ospac policy init --template mobile --output mobile_policy.yaml

# Create custom policy
ospac policy init --output my_policy.yaml
```

**Templates:**
- `mobile` - iOS/Android apps (blocks GPL)
- `desktop` - Desktop applications (allows LGPL with dynamic linking)
- `web` - Web applications (allows most licenses)
- `server` - Server/SaaS applications (blocks AGPL)
- `embedded` - Embedded systems (blocks copyleft)
- `library` - Reusable libraries (permissive only)

#### `ospac policy validate`

Validate policy file syntax.

```bash
# Validate a policy file
ospac policy validate ./my_policy.yaml

# Validate all policies in a directory
ospac policy validate ./policies/
```

### `ospac data`

Manage license database (advanced usage).

**Subcommands:**

#### `ospac data show`

Display license information.

```bash
# Show license details
ospac data show MIT
ospac data show GPL-3.0
ospac data show Apache-2.0

# JSON output
ospac data show MIT -f json
```

#### `ospac data download-spdx`

Download latest SPDX license list.

```bash
ospac data download-spdx
```

#### `ospac data generate`

Generate license database (with optional LLM analysis).

```bash
# Generate with default settings
ospac data generate --output-dir ./data

# Generate with LLM analysis (requires Ollama with llama3)
ospac data generate --use-llm --output-dir ./data
```

#### `ospac data validate`

Validate data integrity.

```bash
# Validate data directory
ospac data validate --data-dir ./data

# Validate with verbose output
ospac data validate --data-dir ./data -v
```

## Python API

### Basic Usage

```python
from ospac import PolicyRuntime

# Initialize with default enterprise policy
runtime = PolicyRuntime()

# Or load custom policies from directory
runtime = PolicyRuntime.from_path("policies/")

# Or load specific policy file
runtime = PolicyRuntime.from_file("mobile_policy.yaml")
```

### Evaluating Licenses

```python
# Basic evaluation
result = runtime.evaluate({
    "licenses_found": ["GPL-3.0", "MIT"],
    "distribution": "commercial"
})

# With additional context
result = runtime.evaluate({
    "licenses_found": ["GPL-2.0", "Apache-2.0"],
    "context": "static_linking",
    "distribution": "mobile"
})

# Check result
if result["action"] == "approve":
    print(f"✓ Approved: {result['message']}")
    print(f"Requirements: {result['requirements']}")
elif result["action"] == "deny":
    print(f"✗ Denied: {result['message']}")
    print(f"Remediation: {result['remediation']}")
else:
    print(f"⚠ Requires review: {result['message']}")
```

**Result Structure:**
```python
{
    "action": "approve|deny|review",
    "severity": "info|warning|error",
    "message": "Human-readable explanation",
    "requirements": ["List of compliance requirements"],
    "remediation": "Suggested fix (if denied)",
    "obligations": {
        "license_id": {
            "permissions": [...],
            "requirements": [...],
            "limitations": [...],
            "obligations": [...]
        }
    }
}
```

### Checking Compatibility

```python
# Basic compatibility check
is_compatible = runtime.check_compatibility("MIT", "GPL-3.0")

# With context
compat_result = runtime.check_compatibility(
    "LGPL-2.1",
    "Apache-2.0",
    context="dynamic_linking"
)

print(f"Compatible: {compat_result['compatible']}")
print(f"Reason: {compat_result['reason']}")
```

### Getting Obligations

```python
# Get obligations for specific licenses
obligations = runtime.get_obligations(["Apache-2.0", "MIT"])

# Access specific license obligations
apache_obligations = obligations["Apache-2.0"]
print(f"Permissions: {apache_obligations['permissions']}")
print(f"Requirements: {apache_obligations['requirements']}")
print(f"Limitations: {apache_obligations['limitations']}")
```

### Advanced API Usage

```python
from ospac import PolicyRuntime, LicenseDatabase

# Load license database directly
db = LicenseDatabase.load()

# Get specific license
license_data = db.get_license("MIT")
print(f"Type: {license_data['type']}")
print(f"Properties: {license_data['properties']}")

# Check all SPDX licenses
all_licenses = db.list_licenses()
print(f"Total licenses: {len(all_licenses)}")

# Filter by license type
permissive_licenses = [
    lic for lic in all_licenses
    if db.get_license(lic)['type'] == 'permissive'
]
```

### Integration with SEMCL.ONE

```python
from osslili import scan_directory
from ospac import PolicyRuntime

# Scan project for licenses
scan_result = scan_directory("/path/to/project")
detected_licenses = scan_result["licenses"]

# Evaluate against policy
runtime = PolicyRuntime.from_file("mobile_policy.yaml")
result = runtime.evaluate({
    "licenses_found": detected_licenses,
    "distribution": "mobile"
})

# Take action based on result
if result["action"] == "deny":
    print("❌ Cannot distribute: License policy violation")
    print(f"Issue: {result['message']}")
    print(f"Fix: {result['remediation']}")
    exit(1)
else:
    print("✓ License compliance check passed")
```

## Policy Files

### Policy File Format

OSPAC uses YAML for policy definitions:

```yaml
version: "1.0"
metadata:
  name: "Mobile App Policy"
  description: "Policy for iOS/Android mobile applications"
  distribution_type: "mobile"

rules:
  - id: block_gpl
    description: "Block GPL licenses for app store compatibility"
    when:
      license_type: copyleft_strong
    then:
      action: deny
      severity: error
      message: "GPL licenses are incompatible with iOS App Store"
      remediation: "Replace with MIT, Apache-2.0, or BSD license"

  - id: allow_permissive
    description: "Allow permissive licenses"
    when:
      license_type: permissive
    then:
      action: approve
      severity: info
      message: "Permissive license approved for mobile distribution"
      requirements:
        - "Include license text in app credits"
        - "Preserve copyright notices"

  - id: review_weak_copyleft
    description: "Review weak copyleft licenses"
    when:
      license_type: copyleft_weak
    then:
      action: review
      severity: warning
      message: "Weak copyleft requires legal review for mobile"
```

### License Data Format (v1.2.0)

OSPAC v1.2.0 uses JSON format for license data:

```json
{
  "license": {
    "id": "Apache-2.0",
    "name": "Apache License 2.0",
    "type": "permissive",
    "spdx_id": "Apache-2.0",

    "properties": {
      "commercial_use": true,
      "distribution": true,
      "modification": true,
      "patent_grant": true,
      "private_use": true
    },

    "requirements": {
      "include_license": true,
      "include_copyright": true,
      "include_notice": true,
      "disclose_source": false,
      "same_license": false,
      "state_changes": true
    },

    "limitations": {
      "liability": false,
      "warranty": false,
      "trademark_use": false
    },

    "obligations": [
      "Include the NOTICE file if provided",
      "State significant changes made to the software",
      "Include the Apache License 2.0 in all distributions",
      "Preserve all copyright, patent, trademark, and attribution notices"
    ],

    "compatibility": {
      "static_linking": {
        "compatible_with": ["MIT", "BSD-3-Clause", "GPL-3.0"],
        "incompatible_with": ["GPL-2.0"],
        "requires_review": []
      },
      "dynamic_linking": {
        "compatible_with": ["MIT", "BSD-3-Clause", "GPL-3.0", "LGPL-2.1"],
        "incompatible_with": [],
        "requires_review": []
      }
    },

    "metadata": {
      "osi_approved": true,
      "fsf_libre": true,
      "category": "permissive",
      "contamination_effect": "none"
    }
  }
}
```

### Understanding License Types

OSPAC classifies licenses into categories:

**Permissive Licenses:**
- `permissive` - MIT, Apache-2.0, BSD variants
- Minimal restrictions
- Can be combined with most other licenses
- Safe for commercial and mobile use

**Copyleft Licenses:**
- `copyleft_weak` - LGPL, MPL (allows dynamic linking)
- `copyleft_strong` - GPL, AGPL (requires source disclosure)
- Require derivative works to use same license
- GPL incompatible with iOS/Android app stores
- AGPL requires source disclosure for network use

**Proprietary Licenses:**
- `proprietary` - Commercial licenses
- Custom terms
- Requires case-by-case evaluation

**Public Domain:**
- `public_domain` - CC0, Unlicense
- No restrictions
- Safe for all uses

## Data Management

### Pre-Built Dataset (v1.2.0)

OSPAC v1.2.0 includes a complete pre-built dataset:

- **712 SPDX licenses** in optimized JSON format
- **Comprehensive metadata** including properties, requirements, limitations
- **Compatibility matrices** for static and dynamic linking
- **Obligation tracking** with license-specific requirements
- **Schema validation** ensuring data integrity

**No setup required!** Works immediately after installation.

### Custom Data Generation (Advanced)

For custom analysis or the latest SPDX data:

```bash
# Download latest SPDX license list
ospac data download-spdx

# Generate basic dataset
ospac data generate --output-dir ./custom_data

# Generate with LLM analysis (requires Ollama with llama3)
ospac data generate --use-llm --output-dir ./custom_data

# Validate generated data
ospac data validate --data-dir ./custom_data
```

### Using Custom Data

Point OSPAC to your custom data directory:

```bash
# Set environment variable
export OSPAC_DATA_DIR=/path/to/custom_data

# Or use command-line option
ospac evaluate -l "MIT" --data-dir /path/to/custom_data
```

In Python:

```python
from ospac import PolicyRuntime, LicenseDatabase

# Load custom database
db = LicenseDatabase.load(data_dir="/path/to/custom_data")

# Use with runtime
runtime = PolicyRuntime(license_db=db)
```

## Integration Patterns

### CI/CD Integration

Add OSPAC to your CI pipeline:

```yaml
# .github/workflows/license-check.yml
name: License Compliance

on: [push, pull_request]

jobs:
  check-licenses:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install OSPAC
        run: pip install "ospac[semcl]"

      - name: Scan for licenses
        run: |
          osslili scan . > licenses.json

      - name: Check compliance
        run: |
          licenses=$(jq -r '.licenses | join(",")' licenses.json)
          ospac evaluate -l "$licenses" -d mobile -f json > result.json

          action=$(jq -r '.action' result.json)
          if [ "$action" == "deny" ]; then
            echo "❌ License compliance failed"
            jq '.message' result.json
            exit 1
          fi

          echo "✓ License compliance passed"
```

### Pre-commit Hook

Add OSPAC to pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: license-check
        name: License Compliance Check
        entry: bash -c 'osslili scan . | jq -r ".licenses | join(\",\")" | xargs -I {} ospac evaluate -l {} -d mobile'
        language: system
        pass_filenames: false
```

### Makefile Integration

Add to your Makefile:

```makefile
.PHONY: license-check
license-check:
	@echo "Checking license compliance..."
	@osslili scan . | jq -r '.licenses | join(",")' | xargs -I {} ospac evaluate -l {} -d mobile
	@echo "✓ License check passed"

.PHONY: license-report
license-report:
	@osslili scan . | jq -r '.licenses | join(",")' | xargs -I {} ospac obligations -l {} -f markdown > LICENSE_OBLIGATIONS.md
	@echo "License report generated: LICENSE_OBLIGATIONS.md"
```

### Docker Integration

Use OSPAC in Docker:

```dockerfile
FROM python:3.9-slim

RUN pip install "ospac[semcl]"

COPY . /app
WORKDIR /app

RUN osslili scan . | jq -r '.licenses | join(",")' | xargs -I {} ospac evaluate -l {} -d commercial

CMD ["python", "app.py"]
```

## Advanced Usage

### Custom Policy Rules

Create sophisticated policy rules:

```yaml
version: "1.0"

rules:
  # Allow specific license combinations
  - id: allow_mit_apache_combo
    when:
      all_licenses:
        - MIT
        - Apache-2.0
    then:
      action: approve

  # Deny GPL with proprietary code
  - id: deny_gpl_proprietary
    when:
      any_licenses:
        - GPL-2.0
        - GPL-3.0
      project_type: proprietary
    then:
      action: deny
      message: "Cannot combine GPL with proprietary code"

  # Context-specific rules
  - id: allow_lgpl_dynamic_only
    when:
      license: LGPL-2.1
      context: dynamic_linking
    then:
      action: approve
      requirements:
        - "Use LGPL code via dynamic linking only"
        - "Allow users to replace LGPL library"
```

### Batch Processing

Process multiple projects:

```python
from ospac import PolicyRuntime
import os
import json

runtime = PolicyRuntime.from_file("mobile_policy.yaml")
results = {}

projects = ["project1", "project2", "project3"]

for project in projects:
    # Scan project
    scan_result = os.popen(f"osslili scan {project}").read()
    licenses = json.loads(scan_result)["licenses"]

    # Evaluate
    result = runtime.evaluate({
        "licenses_found": licenses,
        "distribution": "mobile"
    })

    results[project] = {
        "status": result["action"],
        "message": result["message"]
    }

# Generate report
with open("compliance_report.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Custom License Database

Extend the license database:

```json
{
  "license": {
    "id": "Custom-License-1.0",
    "name": "Custom License 1.0",
    "type": "permissive",
    "spdx_id": "LicenseRef-Custom-1.0",

    "properties": {
      "commercial_use": true,
      "distribution": true,
      "modification": true
    },

    "requirements": {
      "include_license": true,
      "include_copyright": true
    },

    "obligations": [
      "Include custom attribution in documentation"
    ]
  }
}
```

## Troubleshooting

### Common Issues

**Issue: "License not found in database"**

Solution:
```bash
# Check if license ID is valid SPDX identifier
ospac data show YOUR-LICENSE-ID

# If using custom data, ensure it's loaded
export OSPAC_DATA_DIR=/path/to/custom_data
```

**Issue: "Policy file validation failed"**

Solution:
```bash
# Validate policy syntax
ospac policy validate ./my_policy.yaml

# Check YAML formatting
python -c "import yaml; yaml.safe_load(open('my_policy.yaml'))"
```

**Issue: "Compatibility check returns unexpected result"**

Solution:
```bash
# Check compatibility with context
ospac check LICENSE1 LICENSE2 -c static_linking

# View detailed license information
ospac data show LICENSE1 -f json
ospac data show LICENSE2 -f json
```

**Issue: "LLM data generation fails"**

Solution:
```bash
# Ensure Ollama is running
ollama list

# Pull required model
ollama pull llama3

# Try without LLM
ospac data generate --output-dir ./data
```

### Getting Help

1. **Check documentation**: This guide covers most use cases
2. **Validate your inputs**: Use `ospac data show` to verify license IDs
3. **Check policy syntax**: Use `ospac policy validate`
4. **View verbose output**: Add `-v` or `--verbose` to commands
5. **File an issue**: Visit [GitHub Issues](https://github.com/SemClone/ospac/issues)

### Debug Mode

Enable detailed logging:

```bash
# Set log level
export OSPAC_LOG_LEVEL=DEBUG

# Run command
ospac evaluate -l "MIT" -d commercial
```

In Python:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

from ospac import PolicyRuntime

runtime = PolicyRuntime()
# Detailed logs will be output
```

## Additional Resources

- **SPDX License List**: https://spdx.org/licenses/
- **OpenChain Project**: https://www.openchainproject.org/
- **SEMCL.ONE Ecosystem**: https://github.com/SemClone
- **GitHub Repository**: https://github.com/SemClone/ospac
- **Issue Tracker**: https://github.com/SemClone/ospac/issues

## Version History

### v1.2.0 (Latest)
- JSON-first architecture
- Complete SPDX coverage (712 licenses)
- Enhanced policy evaluation
- Build target templates
- 100% test coverage
- Improved compatibility checking

### v1.1.0
- Added LLM analysis support
- Improved obligation tracking
- Enhanced CLI interface

### v1.0.0
- Initial release
- Basic policy evaluation
- License compatibility checking
- YAML policy support
