"""
LLM-based license analyzer using StrandsAgents SDK with Ollama.
Analyzes licenses to extract obligations, compatibility rules, and classifications.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio

# StrandsAgents SDK for LLM integration
try:
    from strandsagents import Agent, OllamaProvider
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("StrandsAgents SDK not installed. Install with: pip install strandsagents")
    Agent = None
    OllamaProvider = None

logger = logging.getLogger(__name__)


class LicenseAnalyzer:
    """
    Analyze licenses using LLM to extract detailed information.
    Uses StrandsAgents SDK with local Ollama running llama3.
    """

    def __init__(self, model: str = "llama3", ollama_url: str = "http://localhost:11434"):
        """
        Initialize the license analyzer.

        Args:
            model: Ollama model to use (default: llama3)
            ollama_url: Ollama server URL
        """
        self.model = model
        self.ollama_url = ollama_url
        self.agent = None

        if Agent and OllamaProvider:
            self._init_agent()
        else:
            logger.error("StrandsAgents SDK not available")

    def _init_agent(self):
        """Initialize the StrandsAgents agent."""
        try:
            provider = OllamaProvider(
                model=self.model,
                base_url=self.ollama_url
            )

            self.agent = Agent(
                name="LicenseAnalyzer",
                provider=provider,
                system_prompt="""You are an expert in software licensing and open source compliance.
                Your task is to analyze software licenses and provide detailed, accurate information about:
                - License obligations and requirements
                - Compatibility with other licenses
                - Usage restrictions and permissions
                - Patent grants and trademark rules

                Always provide information in structured JSON format.
                Be precise and accurate - licensing compliance is critical."""
            )
            logger.info(f"Initialized StrandsAgents with {self.model} at {self.ollama_url}")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            self.agent = None

    async def analyze_license(self, license_id: str, license_text: str) -> Dict[str, Any]:
        """
        Analyze a license using LLM.

        Args:
            license_id: SPDX license identifier
            license_text: Full license text

        Returns:
            Analysis results
        """
        if not self.agent:
            logger.warning(f"Agent not available, returning basic analysis for {license_id}")
            return self._get_fallback_analysis(license_id)

        try:
            # Prepare the analysis prompt
            prompt = f"""Analyze the following license and provide detailed information in JSON format.

License ID: {license_id}
License Text (first 3000 chars):
{license_text[:3000]}

Provide a JSON response with the following structure:
{{
    "license_id": "{license_id}",
    "category": "permissive|copyleft_weak|copyleft_strong|proprietary|public_domain",
    "permissions": {{
        "commercial_use": true/false,
        "distribution": true/false,
        "modification": true/false,
        "patent_grant": true/false,
        "private_use": true/false
    }},
    "conditions": {{
        "disclose_source": true/false,
        "include_license": true/false,
        "include_copyright": true/false,
        "include_notice": true/false,
        "state_changes": true/false,
        "same_license": true/false,
        "network_use_disclosure": true/false
    }},
    "limitations": {{
        "liability": true/false,
        "warranty": true/false,
        "trademark_use": true/false
    }},
    "compatibility": {{
        "can_combine_with_permissive": true/false,
        "can_combine_with_weak_copyleft": true/false,
        "can_combine_with_strong_copyleft": true/false,
        "static_linking_restrictions": "none|weak|strong",
        "dynamic_linking_restrictions": "none|weak|strong"
    }},
    "obligations": [
        "List of specific obligations when using this license"
    ],
    "key_requirements": [
        "List of key requirements for compliance"
    ]
}}"""

            # Query the LLM
            response = await self.agent.query(prompt)

            # Parse the response
            try:
                # Extract JSON from response
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    analysis = json.loads(json_str)
                else:
                    logger.warning(f"Could not extract JSON from LLM response for {license_id}")
                    analysis = self._get_fallback_analysis(license_id)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response for {license_id}: {e}")
                analysis = self._get_fallback_analysis(license_id)

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze {license_id}: {e}")
            return self._get_fallback_analysis(license_id)

    def _get_fallback_analysis(self, license_id: str) -> Dict[str, Any]:
        """
        Get fallback analysis based on known license patterns.

        Args:
            license_id: SPDX license identifier

        Returns:
            Basic analysis results
        """
        # Default analysis structure
        analysis = {
            "license_id": license_id,
            "category": "permissive",
            "permissions": {
                "commercial_use": True,
                "distribution": True,
                "modification": True,
                "patent_grant": False,
                "private_use": True
            },
            "conditions": {
                "disclose_source": False,
                "include_license": True,
                "include_copyright": True,
                "include_notice": False,
                "state_changes": False,
                "same_license": False,
                "network_use_disclosure": False
            },
            "limitations": {
                "liability": True,
                "warranty": True,
                "trademark_use": False
            },
            "compatibility": {
                "can_combine_with_permissive": True,
                "can_combine_with_weak_copyleft": True,
                "can_combine_with_strong_copyleft": False,
                "static_linking_restrictions": "none",
                "dynamic_linking_restrictions": "none"
            },
            "obligations": ["Include license text", "Include copyright notice"],
            "key_requirements": ["Attribution required"]
        }

        # Customize based on known patterns
        if "GPL" in license_id:
            analysis["category"] = "copyleft_strong"
            analysis["conditions"]["disclose_source"] = True
            analysis["conditions"]["same_license"] = True
            analysis["compatibility"]["can_combine_with_strong_copyleft"] = True
            analysis["compatibility"]["can_combine_with_permissive"] = False
            analysis["compatibility"]["static_linking_restrictions"] = "strong"
            analysis["obligations"] = [
                "Disclose source code",
                "Include license text",
                "State changes",
                "Use same license for derivatives"
            ]

        elif "LGPL" in license_id:
            analysis["category"] = "copyleft_weak"
            analysis["conditions"]["disclose_source"] = True
            analysis["compatibility"]["static_linking_restrictions"] = "weak"
            analysis["obligations"] = [
                "Disclose source of LGPL components",
                "Allow relinking",
                "Include license text"
            ]

        elif "AGPL" in license_id:
            analysis["category"] = "copyleft_strong"
            analysis["conditions"]["disclose_source"] = True
            analysis["conditions"]["same_license"] = True
            analysis["conditions"]["network_use_disclosure"] = True
            analysis["compatibility"]["static_linking_restrictions"] = "strong"

        elif "Apache" in license_id:
            analysis["category"] = "permissive"
            analysis["permissions"]["patent_grant"] = True
            analysis["conditions"]["include_notice"] = True
            analysis["conditions"]["state_changes"] = True

        elif "MIT" in license_id or "BSD" in license_id or "ISC" in license_id:
            analysis["category"] = "permissive"

        elif "CC0" in license_id or "Unlicense" in license_id:
            analysis["category"] = "public_domain"
            analysis["conditions"]["include_license"] = False
            analysis["conditions"]["include_copyright"] = False
            analysis["obligations"] = []

        return analysis

    async def extract_compatibility_rules(self, license_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract detailed compatibility rules for a license.

        Args:
            license_id: SPDX license identifier
            analysis: License analysis results

        Returns:
            Compatibility rules
        """
        if not self.agent:
            return self._get_default_compatibility_rules(license_id, analysis)

        try:
            prompt = f"""Based on the {license_id} license with category {analysis.get('category', 'unknown')},
            provide detailed compatibility rules in JSON format:

            {{
                "static_linking": {{
                    "compatible_with": ["list of compatible license IDs or categories"],
                    "incompatible_with": ["list of incompatible license IDs or categories"],
                    "requires_review": ["list of licenses requiring case-by-case review"]
                }},
                "dynamic_linking": {{
                    "compatible_with": ["list"],
                    "incompatible_with": ["list"],
                    "requires_review": ["list"]
                }},
                "distribution": {{
                    "can_distribute_with": ["list"],
                    "cannot_distribute_with": ["list"],
                    "special_requirements": ["list of special requirements"]
                }},
                "contamination_effect": "none|module|derivative|full",
                "notes": "Additional compatibility notes"
            }}"""

            response = await self.agent.query(prompt)

            # Parse response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                rules = json.loads(response[json_start:json_end])
            else:
                rules = self._get_default_compatibility_rules(license_id, analysis)

            return rules

        except Exception as e:
            logger.error(f"Failed to extract compatibility rules for {license_id}: {e}")
            return self._get_default_compatibility_rules(license_id, analysis)

    def _get_default_compatibility_rules(self, license_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get default compatibility rules based on license category."""
        category = analysis.get("category", "permissive")

        if category == "permissive":
            return {
                "static_linking": {
                    "compatible_with": ["category:any"],
                    "incompatible_with": [],
                    "requires_review": []
                },
                "dynamic_linking": {
                    "compatible_with": ["category:any"],
                    "incompatible_with": [],
                    "requires_review": []
                },
                "distribution": {
                    "can_distribute_with": ["category:any"],
                    "cannot_distribute_with": [],
                    "special_requirements": ["Include license and copyright notice"]
                },
                "contamination_effect": "none",
                "notes": "Permissive license with minimal restrictions"
            }

        elif category == "copyleft_strong":
            return {
                "static_linking": {
                    "compatible_with": [license_id, "category:copyleft_strong"],
                    "incompatible_with": ["category:permissive", "category:proprietary"],
                    "requires_review": ["category:copyleft_weak"]
                },
                "dynamic_linking": {
                    "compatible_with": ["category:any"],
                    "incompatible_with": [],
                    "requires_review": ["category:proprietary"]
                },
                "distribution": {
                    "can_distribute_with": [license_id],
                    "cannot_distribute_with": ["category:proprietary"],
                    "special_requirements": ["Source code must be provided", "Same license required"]
                },
                "contamination_effect": "full",
                "notes": "Strong copyleft with viral effect"
            }

        elif category == "copyleft_weak":
            return {
                "static_linking": {
                    "compatible_with": ["category:permissive", license_id],
                    "incompatible_with": [],
                    "requires_review": ["category:copyleft_strong"]
                },
                "dynamic_linking": {
                    "compatible_with": ["category:any"],
                    "incompatible_with": [],
                    "requires_review": []
                },
                "distribution": {
                    "can_distribute_with": ["category:any"],
                    "cannot_distribute_with": [],
                    "special_requirements": ["Allow relinking", "Provide LGPL source"]
                },
                "contamination_effect": "module",
                "notes": "Weak copyleft affecting only the library itself"
            }

        else:
            return {
                "static_linking": {
                    "compatible_with": ["category:any"],
                    "incompatible_with": [],
                    "requires_review": []
                },
                "dynamic_linking": {
                    "compatible_with": ["category:any"],
                    "incompatible_with": [],
                    "requires_review": []
                },
                "distribution": {
                    "can_distribute_with": ["category:any"],
                    "cannot_distribute_with": [],
                    "special_requirements": []
                },
                "contamination_effect": "none",
                "notes": "Default compatibility rules"
            }

    async def batch_analyze(self, licenses: List[Dict[str, Any]], max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """
        Analyze multiple licenses concurrently.

        Args:
            licenses: List of license data with id and text
            max_concurrent: Maximum concurrent analyses

        Returns:
            List of analysis results
        """
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_with_semaphore(license_data):
            async with semaphore:
                license_id = license_data.get("id")
                license_text = license_data.get("text", "")

                logger.info(f"Analyzing {license_id}")

                # Basic analysis
                analysis = await self.analyze_license(license_id, license_text)

                # Extract compatibility rules
                compatibility = await self.extract_compatibility_rules(license_id, analysis)
                analysis["compatibility_rules"] = compatibility

                return analysis

        # Process all licenses
        tasks = [analyze_with_semaphore(lic) for lic in licenses]
        results = await asyncio.gather(*tasks)

        return results