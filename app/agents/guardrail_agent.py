from typing import Dict, Any
from app.utils.pii_masking import has_pii, mask_pii
import re

class GuardrailAgent:
    def __init__(self):
        self.jailbreak_patterns = [
            r"ignore.*instructions",
            r"override.*safety",
            r"bypass.*restrictions",
            r"act as.*uncensored",
            r"developer.*mode"
        ]

    def validate_input(self, content: str) -> Dict[str, Any]:
        """
        Validate input for safety issues.
        """
        issues = []

        # Check for jailbreak attempts
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append("jailbreak_attempt")

        # Check for hate speech (simplified)
        hate_words = ["hate", "racist", "offensive"]  # Expand as needed
        for word in hate_words:
            if word in content.lower():
                issues.append("potential_hate_speech")

        # Check for self-harm indicators
        self_harm_words = ["suicide", "kill myself", "end it all"]
        for word in self_harm_words:
            if word in content.lower():
                issues.append("self_harm_indicator")

        # Check for PII
        if has_pii(content):
            issues.append("contains_pii")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "masked_content": mask_pii(content) if has_pii(content) else content
        }

    def validate_output(self, content: str) -> Dict[str, Any]:
        """
        Validate output for safety and policy compliance.
        """
        issues = []

        # Check for hallucinated content (simplified - would need more sophisticated detection)
        if "I don't know" in content.lower() and len(content.split()) < 10:
            issues.append("potential_hallucination")

        # Check for policy violations
        policy_violations = ["illegal", "harmful", "dangerous"]
        for violation in policy_violations:
            if violation in content.lower():
                issues.append("policy_violation")

        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

    def should_escalate(self, content: str, context: Dict[str, Any] = None) -> bool:
        """
        Determine if query should be escalated to human.
        """
        validation = self.validate_input(content)
        if not validation["valid"]:
            return True

        # Additional escalation logic based on context
        if context and context.get("urgency") == "high":
            return True

        return False