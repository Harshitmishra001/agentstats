import json
from ..recorder import get_recorder

def export_json(filepath: str):
    """
    Exports all completed spans to a JSON file.
    Wraps the array in a versioned schema to support future diffing.
    """
    recorder = get_recorder()
    spans = recorder.get_completed_spans()
    
    report_data = {
        "schema_version": 1,
        "spans": [span.model_dump(mode="json") for span in spans]
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
