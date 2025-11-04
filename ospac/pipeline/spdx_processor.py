"""
SPDX license dataset processor.
Downloads and processes the official SPDX license list.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import yaml
from datetime import datetime

logger = logging.getLogger(__name__)


class SPDXProcessor:
    """Process SPDX license data."""

    SPDX_LICENSE_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
    SPDX_EXCEPTIONS_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/exceptions.json"

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize SPDX processor."""
        self.cache_dir = cache_dir or Path.home() / ".cache" / "ospac" / "spdx"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.licenses = {}
        self.exceptions = {}

    def download_spdx_data(self, force: bool = False) -> Dict[str, Any]:
        """
        Download SPDX license data.

        Args:
            force: Force re-download even if cached

        Returns:
            Dictionary with licenses and exceptions
        """
        licenses_cache = self.cache_dir / "licenses.json"
        exceptions_cache = self.cache_dir / "exceptions.json"

        # Check cache
        if not force and licenses_cache.exists() and exceptions_cache.exists():
            logger.info("Loading SPDX data from cache")
            with open(licenses_cache) as f:
                licenses = json.load(f)
            with open(exceptions_cache) as f:
                exceptions = json.load(f)
        else:
            logger.info("Downloading SPDX license data")

            # Download licenses
            response = requests.get(self.SPDX_LICENSE_URL)
            response.raise_for_status()
            licenses = response.json()

            # Download exceptions
            response = requests.get(self.SPDX_EXCEPTIONS_URL)
            response.raise_for_status()
            exceptions = response.json()

            # Cache the data
            with open(licenses_cache, "w") as f:
                json.dump(licenses, f, indent=2)
            with open(exceptions_cache, "w") as f:
                json.dump(exceptions, f, indent=2)

            logger.info(f"Cached SPDX data to {self.cache_dir}")

        self.licenses = licenses.get("licenses", [])
        self.exceptions = exceptions.get("exceptions", [])

        logger.info(f"Loaded {len(self.licenses)} licenses and {len(self.exceptions)} exceptions")

        return {
            "licenses": self.licenses,
            "exceptions": self.exceptions,
            "version": licenses.get("licenseListVersion"),
            "release_date": licenses.get("releaseDate")
        }

    def get_license_text(self, license_id: str) -> Optional[str]:
        """
        Get the full text of a license.

        Args:
            license_id: SPDX license identifier

        Returns:
            License text or None if not found
        """
        text_cache = self.cache_dir / "texts" / f"{license_id}.txt"

        if text_cache.exists():
            return text_cache.read_text()

        # Find license details URL
        for license_data in self.licenses:
            if license_data.get("licenseId") == license_id:
                details_url = license_data.get("detailsUrl")
                if details_url:
                    try:
                        response = requests.get(details_url)
                        response.raise_for_status()
                        details = response.json()

                        license_text = details.get("licenseText", "")

                        # Cache the text
                        text_cache.parent.mkdir(parents=True, exist_ok=True)
                        text_cache.write_text(license_text)

                        return license_text
                    except Exception as e:
                        logger.error(f"Failed to fetch license text for {license_id}: {e}")

        return None

    def extract_basic_info(self, license_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract basic information from SPDX license data.

        Args:
            license_data: SPDX license data

        Returns:
            Extracted information
        """
        return {
            "id": license_data.get("licenseId"),
            "name": license_data.get("name"),
            "reference": license_data.get("reference"),
            "is_deprecated": license_data.get("isDeprecatedLicenseId", False),
            "is_osi_approved": license_data.get("isOsiApproved", False),
            "is_fsf_libre": license_data.get("isFsfLibre", False),
            "see_also": license_data.get("seeAlso", []),
        }

    def categorize_license(self, license_id: str, license_text: Optional[str] = None) -> str:
        """
        Categorize a license based on its characteristics.

        Args:
            license_id: SPDX license identifier
            license_text: Optional license text

        Returns:
            License category
        """
        # Basic categorization based on known licenses
        categorization = {
            # Permissive
            "MIT": "permissive",
            "Apache-2.0": "permissive",
            "BSD-2-Clause": "permissive",
            "BSD-3-Clause": "permissive",
            "ISC": "permissive",
            "0BSD": "permissive",
            "Unlicense": "public_domain",
            "CC0-1.0": "public_domain",

            # Weak copyleft
            "LGPL-2.1": "copyleft_weak",
            "LGPL-3.0": "copyleft_weak",
            "MPL-2.0": "copyleft_weak",
            "EPL-2.0": "copyleft_weak",
            "CDDL-1.0": "copyleft_weak",

            # Strong copyleft
            "GPL-2.0": "copyleft_strong",
            "GPL-3.0": "copyleft_strong",
            "AGPL-3.0": "copyleft_strong",

            # Proprietary/Commercial
            "Proprietary": "proprietary",
            "Commercial": "proprietary",
        }

        # Check exact match
        if license_id in categorization:
            return categorization[license_id]

        # Check patterns
        if license_id.startswith("MIT"):
            return "permissive"
        elif license_id.startswith("BSD"):
            return "permissive"
        elif license_id.startswith("Apache"):
            return "permissive"
        elif license_id.startswith("GPL"):
            return "copyleft_strong"
        elif license_id.startswith("LGPL"):
            return "copyleft_weak"
        elif license_id.startswith("AGPL"):
            return "copyleft_strong"
        elif license_id.startswith("MPL"):
            return "copyleft_weak"
        elif license_id.startswith("EPL"):
            return "copyleft_weak"
        elif "CC0" in license_id or "Unlicense" in license_id:
            return "public_domain"

        # Default to permissive for unknown
        return "permissive"

    def process_all_licenses(self) -> List[Dict[str, Any]]:
        """
        Process all SPDX licenses.

        Returns:
            List of processed license data
        """
        processed = []

        for license_data in self.licenses:
            license_id = license_data.get("licenseId")
            if not license_id:
                continue

            logger.info(f"Processing {license_id}")

            # Extract basic info
            info = self.extract_basic_info(license_data)

            # Get license text
            license_text = self.get_license_text(license_id)

            # Categorize
            info["category"] = self.categorize_license(license_id, license_text)

            # Add text if available
            if license_text:
                info["has_full_text"] = True
                info["text_length"] = len(license_text)
            else:
                info["has_full_text"] = False

            processed.append(info)

        return processed

    def save_processed_data(self, data: List[Dict[str, Any]], output_dir: Path) -> None:
        """
        Save processed license data to files.

        Args:
            data: Processed license data
            output_dir: Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save as JSON
        json_file = output_dir / "spdx_processed.json"
        with open(json_file, "w") as f:
            json.dump({
                "licenses": data,
                "total": len(data),
                "generated": datetime.now().isoformat(),
                "version": self.licenses[0].get("licenseListVersion") if self.licenses else None
            }, f, indent=2)

        logger.info(f"Saved processed data to {json_file}")

        # Generate summary statistics
        stats = {
            "total_licenses": len(data),
            "categories": {},
            "osi_approved": sum(1 for l in data if l.get("is_osi_approved")),
            "fsf_libre": sum(1 for l in data if l.get("is_fsf_libre")),
            "deprecated": sum(1 for l in data if l.get("is_deprecated")),
            "with_full_text": sum(1 for l in data if l.get("has_full_text"))
        }

        for license_info in data:
            category = license_info.get("category", "unknown")
            stats["categories"][category] = stats["categories"].get(category, 0) + 1

        stats_file = output_dir / "spdx_stats.yaml"
        with open(stats_file, "w") as f:
            yaml.dump(stats, f, default_flow_style=False)

        logger.info(f"Saved statistics to {stats_file}")