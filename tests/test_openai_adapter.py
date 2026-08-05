import pytest
from unittest.mock import MagicMock
import agentstats
from agentstats.recorder import get_recorder

# Mock OpenAI client
class MockUsage:
    def __init__(self, prompt_tokens, completion_tokens):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

class MockResponse:
    def __init__(self):
        self.usage = MockUsage(10, 20)

class MockCompletions:
    def create(self, *args, **kwargs):
        if kwargs.get("model") == "fail-model":
            raise ValueError("OpenAI API Error")
        return MockResponse()
        
class MockAsyncCompletions:
    async def create(self, *args, **kwargs):
        if kwargs.get("model") == "fail-model":
            raise ValueError("OpenAI API Error")
        return MockResponse()

@pytest.fixture
def mock_openai(monkeypatch):
    import agentstats.adapters.openai_compat as compat
    # Force OPENAI_AVAILABLE in case it's not installed
    compat.OPENAI_AVAILABLE = True
    compat._original_create = None
    compat._original_acreate = None
    monkeypatch.setattr(compat, "Completions", MockCompletions)
    monkeypatch.setattr(compat, "AsyncCompletions", MockAsyncCompletions)
    yield compat
    compat.unpatch()

def test_openai_patching(mock_openai):
    recorder = get_recorder()
    recorder.clear()
    
    agentstats.watch()
    
    # Simulate a call
    client = MockCompletions()
    client.create(model="gpt-4o")
    
    spans = recorder.get_completed_spans()
    assert len(spans) == 1
    assert spans[0].tool_name == "openai.chat.completions.create"
    assert spans[0].model == "gpt-4o"
    assert spans[0].tokens_in == 10
    assert spans[0].tokens_out == 20
    assert spans[0].status == "success"
    
def test_openai_error_capture(mock_openai):
    recorder = get_recorder()
    recorder.clear()
    
    agentstats.watch()
    
    client = MockCompletions()
    try:
        client.create(model="fail-model")
    except ValueError:
        pass
        
    spans = recorder.get_completed_spans()
    assert len(spans) == 1
    assert spans[0].status == "error"
    assert spans[0].raw_error == "OpenAI API Error"
