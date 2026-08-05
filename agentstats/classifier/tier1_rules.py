import re
from typing import Optional, Tuple
from ..span import FailureCategory

# Regex patterns for infrastructure errors, designed to be provider-agnostic
# where possible, but covering known OpenAI and Anthropic shapes.
RULES = [
    (
        FailureCategory.INFRA_AUTH_ERROR,
        re.compile(r"(incorrect api key|invalid(_| )api(_| )key|authenticationerror|unauthorized|401)", re.IGNORECASE),
        "Authentication / API key error"
    ),
    (
        FailureCategory.INFRA_RATE_LIMIT,
        re.compile(r"(rate(_| )limit|too many requests|429)", re.IGNORECASE),
        "Rate limit exceeded"
    ),
    (
        FailureCategory.INFRA_TIMEOUT,
        re.compile(r"(timeout|timed out|readtimeout|read_timeout|504)", re.IGNORECASE),
        "Request timed out"
    ),
    (
        FailureCategory.INFRA_MALFORMED_JSON,
        re.compile(r"(jsondecodeerror|expecting value: line|unterminated string|invalid json)", re.IGNORECASE),
        "Malformed JSON response"
    ),
    (
        FailureCategory.INFRA_TOOL_NOT_FOUND,
        re.compile(r"(tool not found|unknown tool|function.*not defined)", re.IGNORECASE),
        "Tool orchestration: Tool not found"
    )
]

def classify_tier1(error_str: str) -> Optional[Tuple[FailureCategory, str]]:
    """
    Attempts to classify an error string using fast regex heuristics.
    Returns a tuple of (FailureCategory, human_readable_reason) if a match is found.
    Returns None if the error doesn't match any Tier 1 infrastructure patterns.
    """
    if not error_str:
        return None
        
    for category, pattern, reason in RULES:
        if pattern.search(error_str):
            # Return the exact matched substring as part of the reason for traceability
            match = pattern.search(error_str)
            matched_text = match.group(0) if match else ""
            return category, f"{reason} (Matched: '{matched_text}')"
            
    return None
