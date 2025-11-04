"""
Policy data generator that produces OSPAC datasets.
Combines SPDX data with LLM analysis to generate comprehensive policy files.
"""

import json
import yaml
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ospac.pipeline.spdx_processor import SPDXProcessor
from ospac.pipeline.llm_analyzer import LicenseAnalyzer

logger = logging.getLogger(__name__)


class PolicyDataGenerator:
    """
    Generate comprehensive policy data from SPDX licenses.
    Produces all required datasets for OSPAC runtime.
    """

    def __init__(self, output_dir: Path = None):
        """
        Initialize the data generator.

        Args:
            output_dir: Output directory for generated data
        """
        self.output_dir = output_dir or Path("data")
        self.spdx_processor = SPDXProcessor()
        self.llm_analyzer = LicenseAnalyzer()

        # Ensure output directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "licenses").mkdir(exist_ok=True)
        (self.output_dir / "compatibility").mkdir(exist_ok=True)
        (self.output_dir / "obligations").mkdir(exist_ok=True)

    async def generate_all_data(self, force_download: bool = False,
                               limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate all policy data from SPDX licenses.

        Args:
            force_download: Force re-download of SPDX data
            limit: Limit number of licenses to process (for testing)

        Returns:
            Summary of generated data
        """
        logger.info("Starting policy data generation")

        # Step 1: Download and process SPDX data
        logger.info("Downloading SPDX license data...")
        spdx_data = self.spdx_processor.download_spdx_data(force=force_download)
        licenses = spdx_data["licenses"]

        if limit:
            licenses = licenses[:limit]
            logger.info(f"Processing limited to {limit} licenses")

        # Step 2: Process licenses with basic categorization
        logger.info(f"Processing {len(licenses)} licenses...")
        processed_licenses = []

        for license_data in licenses:
            license_id = license_data.get("licenseId")
            if not license_id:
                continue

            # Get license text
            license_text = self.spdx_processor.get_license_text(license_id)

            processed_licenses.append({
                "id": license_id,
                "text": license_text or "",
                "spdx_data": license_data
            })

        # Step 3: Analyze licenses with LLM
        logger.info("Analyzing licenses with LLM...")
        analyzed_licenses = await self.llm_analyzer.batch_analyze(processed_licenses)

        # Step 4: Generate policy files
        logger.info("Generating policy files...")
        self._generate_license_policies(analyzed_licenses)
        compatibility_matrix = self._generate_compatibility_matrix(analyzed_licenses)
        obligation_database = self._generate_obligation_database(analyzed_licenses)

        # Step 5: Generate aggregate datasets
        logger.info("Generating aggregate datasets...")
        self._generate_master_database(analyzed_licenses, compatibility_matrix, obligation_database)

        # Step 6: Generate validation data
        validation_report = self._validate_generated_data(analyzed_licenses)

        summary = {
            "total_licenses": len(analyzed_licenses),
            "spdx_version": spdx_data.get("version"),
            "generated_at": datetime.now().isoformat(),
            "output_directory": str(self.output_dir),
            "categories": self._count_categories(analyzed_licenses),
            "validation": validation_report
        }

        # Save summary
        summary_file = self.output_dir / "generation_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Data generation complete. Summary saved to {summary_file}")
        return summary

    def _generate_license_policies(self, licenses: List[Dict[str, Any]]) -> None:
        """Generate individual license policy files."""
        license_dir = self.output_dir / "licenses" / "spdx"
        license_dir.mkdir(parents=True, exist_ok=True)

        for license_data in licenses:
            license_id = license_data.get("license_id")
            if not license_id:
                continue

            # Create policy structure
            policy = {
                "license": {
                    "id": license_id,
                    "name": license_data.get("name", license_id),
                    "type": license_data.get("category", "permissive"),
                    "spdx_id": license_id,

                    "properties": license_data.get("permissions", {}),
                    "requirements": license_data.get("conditions", {}),
                    "limitations": license_data.get("limitations", {}),

                    "compatibility": self._format_compatibility_for_policy(
                        license_data.get("compatibility_rules", {})
                    ),

                    "obligations": license_data.get("obligations", []),
                    "key_requirements": license_data.get("key_requirements", [])
                }
            }

            # Save as YAML
            policy_file = license_dir / f"{license_id}.yaml"
            with open(policy_file, "w") as f:
                yaml.dump(policy, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Generated {len(licenses)} license policy files")

    def _format_compatibility_for_policy(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Format compatibility rules for policy file."""
        return {
            "static_linking": {
                "compatible_with": rules.get("static_linking", {}).get("compatible_with", []),
                "incompatible_with": rules.get("static_linking", {}).get("incompatible_with", []),
                "requires_review": rules.get("static_linking", {}).get("requires_review", [])
            },
            "dynamic_linking": {
                "compatible_with": rules.get("dynamic_linking", {}).get("compatible_with", []),
                "incompatible_with": rules.get("dynamic_linking", {}).get("incompatible_with", []),
                "requires_review": rules.get("dynamic_linking", {}).get("requires_review", [])
            },
            "contamination_effect": rules.get("contamination_effect", "none"),
            "notes": rules.get("notes", "")
        }

    def _generate_compatibility_matrix(self, licenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate license compatibility matrix."""
        matrix = {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "total_licenses": len(licenses),
            "compatibility": {}
        }

        # Build compatibility matrix
        for license1 in licenses:
            id1 = license1.get("license_id")
            if not id1:
                continue

            matrix["compatibility"][id1] = {}

            for license2 in licenses:
                id2 = license2.get("license_id")
                if not id2:
                    continue

                # Determine compatibility
                compat = self._check_license_compatibility(license1, license2)
                matrix["compatibility"][id1][id2] = compat

        # Save matrix
        matrix_file = self.output_dir / "compatibility_matrix.json"
        with open(matrix_file, "w") as f:
            json.dump(matrix, f, indent=2)

        logger.info(f"Generated compatibility matrix: {matrix_file}")
        return matrix

    def _check_license_compatibility(self, license1: Dict, license2: Dict) -> Dict[str, Any]:
        """Check compatibility between two licenses."""
        cat1 = license1.get("category", "permissive")
        cat2 = license2.get("category", "permissive")

        # Basic compatibility rules
        compatibility = {
            "static_linking": "unknown",
            "dynamic_linking": "unknown",
            "distribution": "unknown"
        }

        # Permissive licenses are generally compatible
        if cat1 == "permissive" and cat2 == "permissive":
            compatibility = {
                "static_linking": "compatible",
                "dynamic_linking": "compatible",
                "distribution": "compatible"
            }

        # Strong copyleft contamination
        elif cat1 == "copyleft_strong" or cat2 == "copyleft_strong":
            if cat1 == cat2:
                compatibility = {
                    "static_linking": "compatible",
                    "dynamic_linking": "compatible",
                    "distribution": "compatible"
                }
            else:
                compatibility = {
                    "static_linking": "incompatible",
                    "dynamic_linking": "review_required",
                    "distribution": "incompatible"
                }

        # Weak copyleft
        elif cat1 == "copyleft_weak" or cat2 == "copyleft_weak":
            compatibility = {
                "static_linking": "review_required",
                "dynamic_linking": "compatible",
                "distribution": "compatible"
            }

        return compatibility

    def _generate_obligation_database(self, licenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate obligation database."""
        obligations = {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "licenses": {}
        }

        for license_data in licenses:
            license_id = license_data.get("license_id")
            if not license_id:
                continue

            obligations["licenses"][license_id] = {
                "obligations": license_data.get("obligations", []),
                "key_requirements": license_data.get("key_requirements", []),
                "conditions": license_data.get("conditions", {}),
                "attribution_required": license_data.get("conditions", {}).get("include_copyright", False),
                "source_disclosure_required": license_data.get("conditions", {}).get("disclose_source", False),
                "notice_required": license_data.get("conditions", {}).get("include_notice", False)
            }

        # Save obligations
        obligations_file = self.output_dir / "obligation_database.json"
        with open(obligations_file, "w") as f:
            json.dump(obligations, f, indent=2)

        logger.info(f"Generated obligation database: {obligations_file}")
        return obligations

    def _generate_master_database(self, licenses: List[Dict[str, Any]],
                                 compatibility_matrix: Dict[str, Any],
                                 obligation_database: Dict[str, Any]) -> None:
        """Generate master database with all license information."""
        master_db = {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "total_licenses": len(licenses),
            "licenses": {}
        }

        for license_data in licenses:
            license_id = license_data.get("license_id")
            if not license_id:
                continue

            master_db["licenses"][license_id] = {
                "id": license_id,
                "name": license_data.get("name", license_id),
                "category": license_data.get("category"),
                "permissions": license_data.get("permissions"),
                "conditions": license_data.get("conditions"),
                "limitations": license_data.get("limitations"),
                "obligations": obligation_database["licenses"].get(license_id, {}).get("obligations", []),
                "compatibility_rules": license_data.get("compatibility_rules", {}),
                "spdx_metadata": {
                    "is_osi_approved": license_data.get("spdx_data", {}).get("isOsiApproved", False),
                    "is_fsf_libre": license_data.get("spdx_data", {}).get("isFsfLibre", False),
                    "is_deprecated": license_data.get("spdx_data", {}).get("isDeprecatedLicenseId", False)
                }
            }

        # Save master database
        master_file = self.output_dir / "ospac_license_database.json"
        with open(master_file, "w") as f:
            json.dump(master_db, f, indent=2)

        logger.info(f"Generated master database: {master_file}")

        # Also save as YAML for readability
        master_yaml = self.output_dir / "ospac_license_database.yaml"
        with open(master_yaml, "w") as f:
            yaml.dump(master_db, f, default_flow_style=False)

    def _count_categories(self, licenses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count licenses by category."""
        categories = {}
        for license_data in licenses:
            cat = license_data.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def _validate_generated_data(self, licenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the generated data for completeness and consistency."""
        report = {
            "total_licenses": len(licenses),
            "missing_category": 0,
            "missing_permissions": 0,
            "missing_obligations": 0,
            "missing_compatibility": 0,
            "validation_errors": []
        }

        for license_data in licenses:
            license_id = license_data.get("license_id", "unknown")

            if not license_data.get("category"):
                report["missing_category"] += 1
                report["validation_errors"].append(f"{license_id}: Missing category")

            if not license_data.get("permissions"):
                report["missing_permissions"] += 1
                report["validation_errors"].append(f"{license_id}: Missing permissions")

            if not license_data.get("obligations"):
                report["missing_obligations"] += 1

            if not license_data.get("compatibility_rules"):
                report["missing_compatibility"] += 1

        report["is_valid"] = len(report["validation_errors"]) == 0

        return report