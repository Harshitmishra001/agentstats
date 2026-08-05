import functools
from typing import Any, Callable

try:
    import openai
    from openai.resources.chat.completions import Completions, AsyncCompletions
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..recorder import get_recorder

_original_create = None
_original_acreate = None

def patch():
    """Monkey-patch the OpenAI client to record spans."""
    if not OPENAI_AVAILABLE:
        return

    global _original_create, _original_acreate

    if _original_create is None:
        _original_create = Completions.create
        Completions.create = _patched_create

    if _original_acreate is None:
        _original_acreate = AsyncCompletions.create
        AsyncCompletions.create = _patched_acreate

def unpatch():
    """Remove monkey-patch from the OpenAI client."""
    if not OPENAI_AVAILABLE:
        return

    global _original_create, _original_acreate

    if _original_create is not None:
        Completions.create = _original_create
        _original_create = None

    if _original_acreate is not None:
        AsyncCompletions.create = _original_acreate
        _original_acreate = None

def _extract_usage(response: Any, span: Any):
    """Helper to extract token usage from an OpenAI response."""
    if hasattr(response, 'usage') and response.usage:
        span.tokens_in = getattr(response.usage, 'prompt_tokens', 0)
        span.tokens_out = getattr(response.usage, 'completion_tokens', 0)
        # Cost estimation logic could go here later

@functools.wraps(Completions.create if OPENAI_AVAILABLE else lambda: None)
def _patched_create(self, *args, **kwargs):
    recorder = get_recorder()
    model = kwargs.get("model", "unknown")
    
    with recorder.start_span(tool_name="openai.chat.completions.create", model=model) as span:
        try:
            response = _original_create(self, *args, **kwargs)
            
            # Handle streaming responses vs non-streaming
            if kwargs.get("stream", False):
                # We'll just pass through for now in v1
                # Tracking tokens in streaming requires wrapping the generator
                pass
            else:
                _extract_usage(response, span)
                
            return response
        except Exception as e:
            # Span captures the exception automatically via the context manager
            raise

@functools.wraps(AsyncCompletions.create if OPENAI_AVAILABLE else lambda: None)
async def _patched_acreate(self, *args, **kwargs):
    recorder = get_recorder()
    model = kwargs.get("model", "unknown")
    
    with recorder.start_span(tool_name="openai.chat.completions.create_async", model=model) as span:
        try:
            response = await _original_acreate(self, *args, **kwargs)
            
            if kwargs.get("stream", False):
                pass
            else:
                _extract_usage(response, span)
                
            return response
        except Exception as e:
            raise
