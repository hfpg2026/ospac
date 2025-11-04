# OSPAC Integration Guide

## Overview

This guide covers how to integrate OSPAC into your projects, CI/CD pipelines, and development workflows for automated license compliance.

## Table of Contents

1. [Quick Integration](#quick-integration)
2. [SEMCL.ONE Ecosystem](#semclone-ecosystem)
3. [CI/CD Integration](#cicd-integration)
4. [IDE Integration](#ide-integration)
5. [Docker Integration](#docker-integration)
6. [MCP Integration](#mcp-integration)

## Quick Integration

### Python Project

Add to your project's requirements:

```python
# requirements.txt
ospac>=0.1.0

# Or with extras
ospac[semcl]>=0.1.0  # With SEMCL.ONE tools
ospac[llm]>=0.1.0    # With LLM support
ospac[all]>=0.1.0    # Everything
```

Basic usage script:

```python
#!/usr/bin/env python3
"""check_licenses.py - Check license compliance"""

from ospac import PolicyRuntime
import sys

def check_compliance(licenses, policy_path="policies/"):
    runtime = PolicyRuntime.from_path(policy_path)

    result = runtime.evaluate({
        "licenses_found": licenses,
        "distribution": "commercial",
        "context": "static_linking"
    })

    if not result.is_compliant:
        print("❌ License compliance check failed!")
        for violation in result.violations:
            print(f"  - {violation['message']}")
        return False

    print("✅ License compliance check passed!")
    return True

if __name__ == "__main__":
    # Example: Check specific licenses
    licenses = ["MIT", "Apache-2.0", "BSD-3-Clause"]

    if not check_compliance(licenses):
        sys.exit(1)
```

## SEMCL.ONE Ecosystem

### Complete Compliance Pipeline

Combine all SEMCL.ONE tools for comprehensive compliance:

```python
from osslili import scan_directory
from upmex import extract_metadata
from ospac import PolicyRuntime

class CompliancePipeline:
    """Complete license compliance pipeline."""

    def __init__(self, policy_path="policies/"):
        self.runtime = PolicyRuntime.from_path(policy_path)

    def analyze_project(self, project_path):
        """Analyze project for license compliance."""

        # 1. Detect licenses in source files
        print("Scanning for licenses...")
        scan_results = scan_directory(project_path)
        detected_licenses = [r.spdx_id for r in scan_results.licenses]

        # 2. Extract declared licenses from package files
        print("Extracting package metadata...")
        package_files = ["package.json", "pyproject.toml", "pom.xml"]

        declared_licenses = []
        for pkg_file in package_files:
            pkg_path = f"{project_path}/{pkg_file}"
            try:
                metadata = extract_metadata(pkg_path)
                if metadata.licenses:
                    declared_licenses.extend(metadata.licenses)
            except FileNotFoundError:
                continue

        # 3. Combine all licenses
        all_licenses = list(set(detected_licenses + declared_licenses))
        print(f"Found licenses: {all_licenses}")

        # 4. Evaluate compliance
        print("Evaluating compliance...")
        result = self.runtime.evaluate({
            "licenses_found": all_licenses,
            "distribution": "commercial",
            "context": "static_linking"
        })

        # 5. Generate report
        return self.generate_report(result, all_licenses)

    def generate_report(self, result, licenses):
        """Generate compliance report."""

        report = {
            "compliant": result.is_compliant,
            "licenses": licenses,
            "violations": result.violations,
            "obligations": [],
            "actions_required": result.required_actions
        }

        # Get obligations for each license
        obligations = self.runtime.get_obligations(licenses)
        for license_id, oblig in obligations.items():
            report["obligations"].append({
                "license": license_id,
                "requirements": oblig
            })

        return report

# Usage
pipeline = CompliancePipeline()
report = pipeline.analyze_project("/path/to/project")

if not report["compliant"]:
    print("Project has compliance issues!")
```

### Integration Script

Complete integration script for SEMCL.ONE tools:

```bash
#!/bin/bash
# semcl-check.sh - Complete SEMCL.ONE compliance check

PROJECT_PATH="${1:-.}"

echo "🔍 Running SEMCL.ONE Compliance Check"
echo "======================================"

# Step 1: Detect licenses
echo "Step 1: Detecting licenses..."
osslili "$PROJECT_PATH" -o licenses.json

# Step 2: Extract package metadata
echo "Step 2: Extracting package metadata..."
upmex "$PROJECT_PATH" -o packages.json

# Step 3: Evaluate compliance
echo "Step 3: Evaluating compliance..."
ospac evaluate --licenses $(jq -r '.licenses[].id' licenses.json | tr '\n' ',') \
              --context static_linking \
              --distribution commercial

# Step 4: Generate obligations report
echo "Step 4: Generating obligations..."
ospac obligations --licenses $(jq -r '.licenses[].id' licenses.json | tr '\n' ',') \
                 --format checklist > obligations.txt

echo "✅ Compliance check complete!"
echo "Results saved to: licenses.json, packages.json, obligations.txt"
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/license-compliance.yml
name: License Compliance Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  license-check:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install OSPAC
      run: |
        pip install ospac[semcl]

    - name: Generate/Download Policy Data
      run: |
        # Download if not cached
        if [ ! -d "data" ]; then
          ospac data generate --output-dir ./data
        fi

    - name: Detect Licenses
      run: |
        osslili . -o detected_licenses.json

    - name: Check Compliance
      run: |
        # Extract license IDs and check
        LICENSES=$(python -c "import json; print(','.join([l['id'] for l in json.load(open('detected_licenses.json'))['licenses']]))")
        ospac evaluate --licenses "$LICENSES" --context static_linking

    - name: Generate Report
      if: always()
      run: |
        ospac obligations --licenses "$LICENSES" --format markdown > compliance_report.md

    - name: Upload Report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: compliance-report
        path: compliance_report.md
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - compliance

license_compliance:
  stage: compliance
  image: python:3.11

  before_script:
    - pip install ospac[semcl]
    - ospac data download-spdx

  script:
    - osslili . -o licenses.json
    - |
      LICENSES=$(python -c "import json; print(','.join([l['id'] for l in json.load(open('licenses.json'))['licenses']]))")
      ospac evaluate --licenses "$LICENSES" --distribution commercial

  artifacts:
    when: always
    reports:
      junit: compliance-report.xml
    paths:
      - licenses.json
      - compliance-report.*
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'pip install ospac[semcl]'
                sh 'ospac data download-spdx'
            }
        }

        stage('License Detection') {
            steps {
                sh 'osslili . -o licenses.json'
            }
        }

        stage('Compliance Check') {
            steps {
                script {
                    def licenses = sh(
                        script: "python -c \"import json; print(','.join([l['id'] for l in json.load(open('licenses.json'))['licenses']]))\"",
                        returnStdout: true
                    ).trim()

                    def result = sh(
                        script: "ospac evaluate --licenses ${licenses} --distribution commercial",
                        returnStatus: true
                    )

                    if (result != 0) {
                        error("License compliance check failed!")
                    }
                }
            }
        }

        stage('Generate Report') {
            steps {
                sh 'ospac obligations --licenses ${licenses} --format markdown > report.md'
                archiveArtifacts artifacts: 'report.md', fingerprint: true
            }
        }
    }
}
```

## IDE Integration

### VS Code Task

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Check License Compliance",
      "type": "shell",
      "command": "ospac",
      "args": [
        "evaluate",
        "--licenses", "${input:licenses}",
        "--context", "static_linking"
      ],
      "problemMatcher": [],
      "group": {
        "kind": "test",
        "isDefault": false
      }
    }
  ],
  "inputs": [
    {
      "id": "licenses",
      "type": "promptString",
      "description": "Comma-separated list of licenses",
      "default": "MIT,Apache-2.0"
    }
  ]
}
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: license-compliance
        name: License Compliance Check
        entry: bash -c 'ospac evaluate --licenses $(osslili . --format json | jq -r ".licenses[].id" | tr "\n" ",")'
        language: system
        pass_filenames: false
        always_run: true
```

## Docker Integration

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install OSPAC with all features
RUN pip install ospac[all]

# Generate policy data
RUN ospac data generate --output-dir /data

# Set up working directory
WORKDIR /app

# Copy compliance script
COPY check_compliance.py .

# Default command
CMD ["python", "check_compliance.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  license-checker:
    build: .
    volumes:
      - ./:/workspace
      - ospac-data:/data
    environment:
      - OSPAC_POLICY_PATH=/data/policies
    command: >
      sh -c "
        osslili /workspace -o /tmp/licenses.json &&
        ospac evaluate --licenses $$(cat /tmp/licenses.json | jq -r '.licenses[].id' | tr '\n' ',')
      "

volumes:
  ospac-data:
```

## MCP Integration

### Model Context Protocol Server

```python
# mcp_server.py
from mcp import Server, Tool
from ospac import PolicyRuntime
import json

class LicenseComplianceServer(Server):
    """MCP server for license compliance checking."""

    def __init__(self):
        super().__init__("license-compliance")
        self.runtime = PolicyRuntime.from_path("data/policies")

    @Tool("check_license_compliance")
    async def check_compliance(self, licenses: list, context: str = "general"):
        """Check if licenses are compliant with policy."""

        result = self.runtime.evaluate({
            "licenses_found": licenses,
            "context": context,
            "distribution": "commercial"
        })

        return {
            "compliant": result.is_compliant,
            "violations": result.violations,
            "warnings": result.warnings,
            "required_actions": result.required_actions
        }

    @Tool("get_license_obligations")
    async def get_obligations(self, licenses: list):
        """Get obligations for specified licenses."""

        obligations = self.runtime.get_obligations(licenses)

        return {
            "obligations": obligations,
            "total_licenses": len(licenses)
        }

    @Tool("check_compatibility")
    async def check_compatibility(self, license1: str, license2: str, context: str = "general"):
        """Check if two licenses are compatible."""

        result = self.runtime.check_compatibility(license1, license2, context)

        return {
            "compatible": result.is_compliant,
            "details": result.to_dict()
        }

# Run server
if __name__ == "__main__":
    server = LicenseComplianceServer()
    server.run()
```

### Using with LLM

```python
# Use the MCP server with an LLM
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    max_tokens=1000,
    tools=[
        {
            "type": "mcp",
            "server": "license-compliance",
            "tool": "check_license_compliance"
        }
    ],
    messages=[{
        "role": "user",
        "content": "Check if MIT and GPL-3.0 are compatible for static linking"
    }]
)
```

## Best Practices

1. **Cache Policy Data**: Generate once, use many times
2. **Version Control Policies**: Keep policies in Git
3. **Automate Checks**: Integrate into CI/CD
4. **Regular Updates**: Update SPDX data monthly
5. **Custom Policies**: Extend templates for your needs
6. **Monitor Changes**: Alert on new license detections
7. **Document Decisions**: Keep audit trail of approvals

## Troubleshooting

### Common Issues

1. **No policy data found**
   ```bash
   ospac data generate --output-dir ./data
   ```

2. **LLM not working**
   ```bash
   # Ensure Ollama is running
   ollama serve
   ollama pull llama3
   ```

3. **Import errors**
   ```bash
   pip install ospac[all] --upgrade
   ```

## Support

- GitHub Issues: https://github.com/SemClone/ospac/issues
- Documentation: https://github.com/SemClone/ospac/docs
- SEMCL.ONE Project: https://github.com/SemClone