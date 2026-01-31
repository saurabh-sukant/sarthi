import re
from typing import List

class PIIMasker:
    """Simple PII masking utility."""

    def __init__(self):
        # Patterns for common PII
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        }

    def mask_text(self, text: str) -> str:
        """Mask PII in text."""
        masked_text = text
        for pii_type, pattern in self.patterns.items():
            masked_text = re.sub(pattern, f'[MASKED_{pii_type.upper()}]', masked_text)
        return masked_text

    def contains_pii(self, text: str) -> bool:
        """Check if text contains PII."""
        for pattern in self.patterns.values():
            if re.search(pattern, text):
                return True
        return False

# Global instance
pii_masker = PIIMasker()

def mask_pii(text: str) -> str:
    """Convenience function to mask PII."""
    return pii_masker.mask_text(text)

def has_pii(text: str) -> bool:
    """Convenience function to check for PII."""
    return pii_masker.contains_pii(text)