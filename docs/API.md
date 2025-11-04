# OSPAC API Documentation

## Installation

```bash
# Basic installation
pip install ospac

# With SEMCL.ONE integration
pip install "ospac[semcl]"

# With LLM support
pip install "ospac[llm]"

# Full installation
pip install "ospac[all]"
```

## Core Classes

### PolicyRuntime

The main runtime engine for policy evaluation.

```python
from ospac import PolicyRuntime

# Initialize with policy directory
runtime = PolicyRuntime("policies/")

# Or use factory method
runtime = PolicyRuntime.from_path("policies/")
```

#### Methods

##### `evaluate(context: dict) -> PolicyResult`

Evaluate context against loaded policies.

```python
result = runtime.evaluate({
    "licenses_found": ["MIT", "Apache-2.0"],
    "context": "static_linking",
    "distribution": "commercial"
})

if result.action == "allow":
    print("Licenses approved")
else:
    print(f"Issue: {result.message}")
```

##### `check_compatibility(license1: str, license2: str, context: str) -> ComplianceResult`

Check if two licenses are compatible.

```python
result = runtime.check_compatibility("MIT", "GPL-3.0", "static_linking")

if result.is_compliant:
    print("Licenses are compatible")
else:
    for violation in result.violations:
        print(f"Violation: {violation['message']}")
```

##### `get_obligations(licenses: list) -> dict`

Get obligations for specified licenses.

```python
obligations = runtime.get_obligations(["Apache-2.0", "MIT"])

for license_id, oblig in obligations.items():
    print(f"{license_id}: {oblig}")
```

### License Model

Represents a software license with its properties.

```python
from ospac.models import License

# Create license instance
license = License(
    id="MIT",
    name="MIT License",
    type="permissive",
    spdx_id="MIT",
    properties={
        "commercial_use": True,
        "distribution": True
    },
    requirements={
        "include_license": True,
        "include_copyright": True
    }
)

# Check compatibility
other = License(id="Apache-2.0", type="permissive")
is_compatible = license.is_compatible_with(other, "static_linking")

# Get obligations
obligations = license.get_obligations()
# Returns: ["Include license text", "Include copyright notice"]
```

### Policy Model

Represents compliance policies with rules.

```python
from ospac.models import Policy, Rule

# Create policy
policy = Policy(name="Enterprise", version="1.0")

# Add rules
rule = Rule(
    id="no_gpl",
    description="No GPL in products",
    when={"license_type": "copyleft_strong"},
    then={
        "action": "deny",
        "severity": "error",
        "message": "GPL not allowed in commercial products"
    },
    priority=100
)

policy.add_rule(rule)

# Evaluate against context
results = policy.evaluate({
    "license_type": "copyleft_strong",
    "distribution": "commercial"
})
```

### ComplianceResult

Results from compliance evaluation.

```python
from ospac.models import ComplianceResult

# Check result status
if result.is_compliant:
    print("All licenses compliant")
elif result.needs_review:
    print("Manual review required")
else:
    print("Compliance violations found")

# Access violations and warnings
for violation in result.violations:
    print(f"Error: {violation['message']}")

for warning in result.warnings:
    print(f"Warning: {warning['message']}")

# Get required actions
for action in result.required_actions:
    print(f"Required: {action}")
```

## Data Pipeline API

### SPDXProcessor

Process SPDX license data.

```python
from ospac.pipeline import SPDXProcessor

processor = SPDXProcessor()

# Download SPDX data
data = processor.download_spdx_data(force=False)
print(f"Loaded {len(data['licenses'])} licenses")

# Get license text
text = processor.get_license_text("MIT")

# Categorize license
category = processor.categorize_license("GPL-3.0")
# Returns: "copyleft_strong"

# Process all licenses
processed = processor.process_all_licenses()

# Save processed data
processor.save_processed_data(processed, Path("output"))
```

### LicenseAnalyzer

Analyze licenses with LLM support.

```python
import asyncio
from ospac.pipeline import LicenseAnalyzer

analyzer = LicenseAnalyzer(model="llama3")

async def analyze():
    # Analyze single license
    analysis = await analyzer.analyze_license("MIT", license_text)

    # Extract compatibility rules
    rules = await analyzer.extract_compatibility_rules("MIT", analysis)

    # Batch analyze multiple licenses
    results = await analyzer.batch_analyze([
        {"id": "MIT", "text": "..."},
        {"id": "Apache-2.0", "text": "..."}
    ])

    return results

# Run async function
results = asyncio.run(analyze())
```

### PolicyDataGenerator

Generate complete policy datasets.

```python
import asyncio
from ospac.pipeline import PolicyDataGenerator

generator = PolicyDataGenerator(output_dir=Path("data"))

async def generate():
    # Generate all data
    summary = await generator.generate_all_data(
        force_download=False,
        limit=None  # Process all licenses
    )

    print(f"Generated data for {summary['total_licenses']} licenses")
    print(f"Categories: {summary['categories']}")

    return summary

# Run generation
summary = asyncio.run(generate())
```

## Integration Examples

### With osslili (License Detection)

```python
from osslili import scan_directory
from ospac import PolicyRuntime

# Detect licenses in project
licenses = scan_directory("/path/to/project")

# Extract license IDs
license_ids = [lic.spdx_id for lic in licenses]

# Evaluate against policy
runtime = PolicyRuntime.from_path("policies/")
result = runtime.evaluate({
    "licenses_found": license_ids,
    "distribution": "commercial",
    "context": "static_linking"
})

if not result.is_compliant:
    print("Compliance issues found!")
    for violation in result.violations:
        print(f"- {violation['message']}")
```

### With upmex (Package Extraction)

```python
from upmex import extract_metadata
from ospac import PolicyRuntime

# Extract package metadata
metadata = extract_metadata("package.json")

# Get declared licenses
licenses = metadata.get("licenses", [])

# Check compliance
runtime = PolicyRuntime.from_path("policies/")
for license_id in licenses:
    obligations = runtime.get_obligations([license_id])
    print(f"{license_id} obligations: {obligations}")
```

### In CI/CD Pipeline

```python
import sys
from ospac import PolicyRuntime

def check_license_compliance(project_path: str, policy: str):
    """Check license compliance in CI/CD."""

    # Load policy
    runtime = PolicyRuntime.from_path(policy)

    # Detect licenses (using osslili or other tool)
    licenses = detect_licenses(project_path)

    # Evaluate
    result = runtime.evaluate({
        "licenses_found": licenses,
        "distribution": "commercial"
    })

    # Exit with error if non-compliant
    if not result.is_compliant:
        print("License compliance check failed!")
        for v in result.violations:
            print(f"ERROR: {v['message']}")
        sys.exit(1)

    print("License compliance check passed!")
    return True
```

## Async Operations

Many operations support async for better performance:

```python
import asyncio
from ospac.pipeline import LicenseAnalyzer, PolicyDataGenerator

async def main():
    # Parallel analysis
    analyzer = LicenseAnalyzer()

    licenses = [
        {"id": "MIT", "text": "..."},
        {"id": "Apache-2.0", "text": "..."},
        {"id": "GPL-3.0", "text": "..."}
    ]

    # Analyze all in parallel (max 5 concurrent)
    results = await analyzer.batch_analyze(licenses, max_concurrent=5)

    return results

# Run async
results = asyncio.run(main())
```

## Error Handling

```python
from ospac import PolicyRuntime
from ospac.exceptions import PolicyError, ValidationError

try:
    runtime = PolicyRuntime.from_path("policies/")
    result = runtime.evaluate(context)

except FileNotFoundError:
    print("Policy files not found")

except ValidationError as e:
    print(f"Invalid policy: {e}")

except PolicyError as e:
    print(f"Policy evaluation failed: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

```python
# Custom configuration
from ospac import PolicyRuntime

runtime = PolicyRuntime()

# Load policies from multiple sources
runtime.load_policies("policies/base")
runtime.load_policies("policies/custom")

# Set evaluation options
runtime.options = {
    "strict_mode": True,
    "allow_deprecated": False,
    "log_decisions": True
}
```

## Testing

```python
import pytest
from ospac import PolicyRuntime

@pytest.fixture
def runtime():
    return PolicyRuntime.from_path("test_policies/")

def test_mit_allowed(runtime):
    result = runtime.evaluate({
        "licenses_found": ["MIT"],
        "distribution": "commercial"
    })
    assert result.is_compliant

def test_gpl_denied(runtime):
    result = runtime.evaluate({
        "licenses_found": ["GPL-3.0"],
        "distribution": "commercial",
        "context": "static_linking"
    })
    assert not result.is_compliant
```

## Performance Tips

1. **Cache policy files**: Load once, evaluate many times
2. **Use batch operations**: Process multiple licenses together
3. **Enable async**: Use async methods for I/O operations
4. **Pre-generate data**: Generate datasets once, query many times
5. **Limit scope**: Use `--limit` flag during development

## Debugging

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now operations will show debug info
runtime = PolicyRuntime.from_path("policies/")
```