import pytest
from unittest.mock import MagicMock
import agentstats
from agentstats.recorder import get_recorder

class MockUsage:
    def __init__(self, input_tokens, output_tokens):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

class MockResponse:
    def __init__(self):
        self.usage = MockUsage(15, 25)

class MockMessages:
    def create(self, *args, **kwargs):
        if kwargs.get("model") == "fail-model":
            raise ValueError("Anthropic API Error")
        return MockResponse()
        
class MockAsyncMessages:
    async def create(self, *args, **kwargs):
        if kwargs.get("model") == "fail-model":
            raise ValueError("Anthropic API Error")
        return MockResponse()

@pytest.fixture
def mock_anthropic(monkeypatch):
    import agentstats.adapters.anthropic_compat as compat
    monkeypatch.setattr(compat, "ANTHROPIC_AVAILABLE", True)
    compat._original_create = None
    compat._original_acreate = None
    # Since Messages doesn't exist if anthropic isn't installed, we set it manually
    setattr(compat, "Messages", MockMessages)
    setattr(compat, "AsyncMessages", MockAsyncMessages)
    
    yield compat
    
    # Cleanup after test
    compat.unpatch()
    
    if hasattr(compat, "Messages"):
        delattr(compat, "Messages")
    if hasattr(compat, "AsyncMessages"):
        delattr(compat, "AsyncMessages")

def test_anthropic_patching(mock_anthropic):
    recorder = get_recorder()
    recorder.clear()
    
    agentstats.watch()
    
    client = MockMessages()
    client.create(model="claude-3-5-sonnet")
    
    spans = recorder.get_completed_spans()
    assert len(spans) == 1
    assert spans[0].tool_name == "anthropic.messages.create"
    assert spans[0].model == "claude-3-5-sonnet"
    assert spans[0].tokens_in == 15
    assert spans[0].tokens_out == 25
    assert spans[0].status == "success"

def test_anthropic_error_capture(mock_anthropic):
    recorder = get_recorder()
    recorder.clear()
    
    agentstats.watch()
    
    client = MockMessages()
    try:
        client.create(model="fail-model")
    except ValueError:
        pass
        
    spans = recorder.get_completed_spans()
    assert len(spans) == 1
    assert spans[0].status == "error"
    assert spans[0].raw_error == "Anthropic API Error"
