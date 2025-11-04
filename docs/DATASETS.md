# OSPAC Datasets Documentation

## Overview

OSPAC generates and uses several datasets to provide comprehensive license compliance analysis. All datasets are generated from the official SPDX license list and can be enhanced with LLM analysis.

## Generated Datasets

### 1. Master License Database (`ospac_license_database.json`)

The primary database containing all license information:

```json
{
  "version": "1.0",
  "generated": "2024-01-01T00:00:00",
  "licenses": {
    "MIT": {
      "id": "MIT",
      "name": "MIT License",
      "category": "permissive",
      "permissions": {
        "commercial_use": true,
        "distribution": true,
        "modification": true,
        "patent_grant": false,
        "private_use": true
      },
      "conditions": {
        "include_license": true,
        "include_copyright": true,
        "disclose_source": false,
        "same_license": false
      },
      "obligations": [
        "Include license text",
        "Include copyright notice"
      ],
      "compatibility_rules": {...},
      "spdx_metadata": {...}
    }
  }
}
```

**Fields:**
- `category`: License type (permissive, copyleft_weak, copyleft_strong, proprietary, public_domain)
- `permissions`: What the license allows
- `conditions`: Requirements that must be met
- `obligations`: Specific compliance obligations
- `compatibility_rules`: Detailed compatibility information

### 2. Compatibility Matrix (`compatibility_matrix.json`)

Pre-computed compatibility between all license pairs:

```json
{
  "compatibility": {
    "MIT": {
      "Apache-2.0": {
        "static_linking": "compatible",
        "dynamic_linking": "compatible",
        "distribution": "compatible"
      },
      "GPL-3.0": {
        "static_linking": "incompatible",
        "dynamic_linking": "review_required",
        "distribution": "incompatible"
      }
    }
  }
}
```

**Compatibility Values:**
- `compatible`: Licenses can be combined
- `incompatible`: Licenses cannot be combined
- `review_required`: Case-by-case legal review needed
- `unknown`: Compatibility not determined

### 3. Obligation Database (`obligation_database.json`)

Detailed obligations for each license:

```json
{
  "licenses": {
    "Apache-2.0": {
      "obligations": [
        "Include license text",
        "Include copyright notice",
        "Include NOTICE file if present",
        "State changes in modified files"
      ],
      "key_requirements": [
        "Patent grant included",
        "Trademark use restricted"
      ],
      "attribution_required": true,
      "source_disclosure_required": false,
      "notice_required": true
    }
  }
}
```

### 4. Policy Files (`policies/`)

YAML files defining license characteristics and rules:

```yaml
# policies/licenses/spdx/MIT.yaml
license:
  id: MIT
  type: permissive
  requirements:
    include_license: true
    include_copyright: true
  compatibility:
    static_linking:
      compatible_with: [category:any]
```

## Generating Datasets

### Basic Generation

Generate datasets without LLM enhancement:

```bash
# Download SPDX data
ospac data download-spdx

# Generate all datasets
ospac data generate --output-dir ./data
```

### LLM-Enhanced Generation

For more accurate categorization and compatibility analysis:

```bash
# Requires Ollama running with llama3 model
ospac data generate --use-llm --output-dir ./data
```

### Limiting Scope (for testing)

```bash
# Process only first 10 licenses
ospac data generate --limit 10 --output-dir ./test-data
```

## Querying Datasets

### CLI Queries

```bash
# Show specific license details
ospac data show MIT

# Output in different formats
ospac data show Apache-2.0 --format json
ospac data show GPL-3.0 --format yaml

# Validate dataset integrity
ospac data validate --data-dir ./data
```

### Python API Queries

```python
import json
from pathlib import Path

# Load master database
with open("data/ospac_license_database.json") as f:
    db = json.load(f)

# Query specific license
mit = db["licenses"]["MIT"]
print(f"Category: {mit['category']}")
print(f"Obligations: {mit['obligations']}")

# Check compatibility
with open("data/compatibility_matrix.json") as f:
    compat = json.load(f)

mit_gpl = compat["compatibility"]["MIT"]["GPL-3.0"]
print(f"MIT + GPL-3.0 static linking: {mit_gpl['static_linking']}")
```

## Dataset Structure

```
data/
├── ospac_license_database.json     # Master database
├── ospac_license_database.yaml     # Same in YAML format
├── compatibility_matrix.json       # License compatibility
├── obligation_database.json        # Compliance obligations
├── spdx_processed.json             # Raw SPDX data
├── spdx_stats.yaml                 # Statistics
├── generation_summary.json         # Generation metadata
└── licenses/
    └── spdx/
        ├── MIT.yaml                # Individual license policies
        ├── Apache-2.0.yaml
        └── ...
```

## Data Sources

- **Primary**: [SPDX License List](https://spdx.org/licenses/)
- **Version**: Automatically uses latest SPDX release
- **Updates**: Re-generate periodically to get new licenses

## Validation

Always validate generated data:

```bash
ospac data validate
```

This checks for:
- Missing required fields
- Data consistency
- License categorization
- Obligation completeness

## Customization

### Adding Custom Licenses

Create a YAML file in `policies/licenses/custom/`:

```yaml
license:
  id: CUSTOM-1.0
  name: "Custom License 1.0"
  type: proprietary
  requirements:
    written_permission: true
```

### Modifying Categorization

Edit the `categorize_license()` method in `ospac/pipeline/spdx_processor.py` to adjust how licenses are categorized.

## Performance

- Full SPDX dataset: ~700 licenses
- Generation time (without LLM): ~1 minute
- Generation time (with LLM): ~10-30 minutes
- Dataset size: ~5-10 MB

## Caching

Generated data is cached in:
- `~/.cache/ospac/spdx/` - Downloaded SPDX data
- `data/` - Generated datasets

Force regeneration with:
```bash
ospac data generate --force
```