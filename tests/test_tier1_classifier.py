import pytest
from agentstats.classifier.tier1_rules import classify_tier1
from agentstats.span import FailureCategory

def test_classify_tier1_openai_auth_error():
    error_str = "AuthenticationError: Error code: 401 - {'error': {'message': 'Incorrect API key provided'}}"
    result = classify_tier1(error_str)
    
    assert result is not None
    category, reason = result
    assert category == FailureCategory.INFRA_AUTH_ERROR
    assert "Matched: 'AuthenticationError'" in reason

def test_classify_tier1_anthropic_auth_error():
    # Anthropic often uses "unauthorized" or "authentication"
    error_str = "anthropic.AuthenticationError: invalid x-api-key"
    result = classify_tier1(error_str)
    
    assert result is not None
    assert result[0] == FailureCategory.INFRA_AUTH_ERROR
    
    error_str2 = "401 Unauthorized"
    result2 = classify_tier1(error_str2)
    assert result2 is not None
    assert result2[0] == FailureCategory.INFRA_AUTH_ERROR

def test_classify_tier1_timeout():
    error_str = "requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='api.openai.com', port=443): Read timed out."
    result = classify_tier1(error_str)
    assert result is not None
    assert result[0] == FailureCategory.INFRA_TIMEOUT

def test_classify_tier1_rate_limit():
    error_str = "anthropic.RateLimitError: 429 Too Many Requests"
    result = classify_tier1(error_str)
    assert result is not None
    assert result[0] == FailureCategory.INFRA_RATE_LIMIT
    
def test_classify_tier1_unmatched_error():
    error_str = "Some logical error that doesn't match any regex"
    result = classify_tier1(error_str)
    assert result is None
