import uuid
import time
from typing import Optional, List, Dict
from contextvars import ContextVar
import threading
from contextlib import contextmanager

from .span import Span

# Context variable for tracking the current span ID.
# This works seamlessly with asyncio and threads (if copied context is used).
current_span_id: ContextVar[Optional[str]] = ContextVar("current_span_id", default=None)

class Recorder:
    def __init__(self):
        self._lock = threading.Lock()
        self.spans: Dict[str, Span] = {}
        self.completed_spans: List[Span] = []

    @contextmanager
    def start_span(self, tool_name: str, model: Optional[str] = None):
        """Start a new span, automatically setting parent_id from the context."""
        span_id = str(uuid.uuid4())
        parent_id = current_span_id.get()
        
        span = Span(
            id=span_id,
            parent_id=parent_id,
            tool_name=tool_name,
            model=model,
            start_ts=time.time()
        )
        
        with self._lock:
            self.spans[span_id] = span
            
        # Set the current span for any nested calls within this block
        token = current_span_id.set(span_id)
        
        try:
            yield span
        except Exception as e:
            span.status = "error"
            span.raw_error = str(e)
            
            # Non-blocking Tier 1 classification
            from .classifier import classify_tier1
            classification = classify_tier1(span.raw_error)
            if classification:
                span.failure_category = classification[0]
                span.failure_reason = classification[1]
            
            raise
        finally:
            # End the span
            span.end_ts = time.time()
            if span.status == "running":
                span.status = "success"
                
            with self._lock:
                self.completed_spans.append(span)
                # optionally remove from self.spans if we only want active ones there
                
            # Restore the previous context
            current_span_id.reset(token)

    def get_completed_spans(self) -> List[Span]:
        with self._lock:
            return list(self.completed_spans)

    def clear(self):
        with self._lock:
            self.spans.clear()
            self.completed_spans.clear()

# Global recorder instance
_recorder = Recorder()

def get_recorder() -> Recorder:
    return _recorder
