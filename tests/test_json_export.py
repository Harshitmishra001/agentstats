import json
import os
from agentstats.recorder import get_recorder
from agentstats.export import export_json

def test_json_export_schema(tmp_path):
    recorder = get_recorder()
    recorder.clear()
    
    with recorder.start_span("test_tool_1", "model_1") as span:
        span.tokens_in = 100
        span.tokens_out = 50
        
    export_path = tmp_path / "export.json"
    export_json(str(export_path))
    
    assert export_path.exists()
    
    with open(export_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "schema_version" in data
    assert data["schema_version"] == 1
    assert "spans" in data
    assert len(data["spans"]) == 1
    
    exported_span = data["spans"][0]
    assert exported_span["tool_name"] == "test_tool_1"
    assert exported_span["model"] == "model_1"
    assert exported_span["tokens_in"] == 100
    assert exported_span["status"] == "success"
