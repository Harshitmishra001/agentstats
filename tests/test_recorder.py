import pytest
import asyncio
from agentstats.recorder import get_recorder

def test_recorder_basic():
    recorder = get_recorder()
    recorder.clear()
    
    with recorder.start_span("test_tool", "test_model") as span:
        span.tokens_in = 10
        span.tokens_out = 20
        
    spans = recorder.get_completed_spans()
    assert len(spans) == 1
    assert spans[0].tool_name == "test_tool"
    assert spans[0].model == "test_model"
    assert spans[0].tokens_in == 10
    assert spans[0].tokens_out == 20
    assert spans[0].status == "success"

def test_recorder_error_capture():
    recorder = get_recorder()
    recorder.clear()
    
    try:
        with recorder.start_span("failing_tool") as span:
            raise ValueError("Test error")
    except ValueError:
        pass
        
    spans = recorder.get_completed_spans()
    assert len(spans) == 1
    assert spans[0].status == "error"
    assert spans[0].raw_error == "Test error"

def test_recorder_nesting():
    recorder = get_recorder()
    recorder.clear()
    
    with recorder.start_span("parent") as parent:
        with recorder.start_span("child") as child:
            pass
            
    spans = recorder.get_completed_spans()
    assert len(spans) == 2
    
    child_span = next(s for s in spans if s.tool_name == "child")
    parent_span = next(s for s in spans if s.tool_name == "parent")
    
    assert child_span.parent_id == parent_span.id

@pytest.mark.asyncio
async def test_recorder_async_nesting():
    recorder = get_recorder()
    recorder.clear()
    
    async def sub_task():
        with recorder.start_span("async_child"):
            pass
            
    with recorder.start_span("async_parent") as parent:
        await asyncio.gather(sub_task(), sub_task())
        
    spans = recorder.get_completed_spans()
    assert len(spans) == 3
    
    parent_span = next(s for s in spans if s.tool_name == "async_parent")
    children = [s for s in spans if s.tool_name == "async_child"]
    
    assert len(children) == 2
    assert children[0].parent_id == parent_span.id
    assert children[1].parent_id == parent_span.id
