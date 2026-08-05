import functools
from typing import Any

try:
    import anthropic
    from anthropic.resources.messages import Messages, AsyncMessages
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from ..recorder import get_recorder

_original_create = None
_original_acreate = None

def patch():
    """Monkey-patch the Anthropic client to record spans."""
    if not ANTHROPIC_AVAILABLE:
        return

    global _original_create, _original_acreate

    if _original_create is None:
        _original_create = Messages.create
        Messages.create = _patched_create

    if _original_acreate is None:
        _original_acreate = AsyncMessages.create
        AsyncMessages.create = _patched_acreate

def unpatch():
    """Remove monkey-patch from the Anthropic client."""
    if not ANTHROPIC_AVAILABLE:
        return

    global _original_create, _original_acreate

    if _original_create is not None:
        Messages.create = _original_create
        _original_create = None

    if _original_acreate is not None:
        AsyncMessages.create = _original_acreate
        _original_acreate = None

def _extract_usage(response: Any, span: Any):
    """Helper to extract token usage from an Anthropic response."""
    if hasattr(response, 'usage') and response.usage:
        span.tokens_in = getattr(response.usage, 'input_tokens', 0)
        span.tokens_out = getattr(response.usage, 'output_tokens', 0)

@functools.wraps(Messages.create if ANTHROPIC_AVAILABLE else lambda: None)
def _patched_create(self, *args, **kwargs):
    recorder = get_recorder()
    model = kwargs.get("model", "unknown")
    
    with recorder.start_span(tool_name="anthropic.messages.create", model=model) as span:
        try:
            response = _original_create(self, *args, **kwargs)
            
            # Anthropic streaming is handled differently, skip usage extraction for streams in v1
            if kwargs.get("stream", False):
                pass
            else:
                _extract_usage(response, span)
                
            return response
        except Exception as e:
            # Span captures the exception and Tier 1 logic runs automatically in recorder
            raise

@functools.wraps(AsyncMessages.create if ANTHROPIC_AVAILABLE else lambda: None)
async def _patched_acreate(self, *args, **kwargs):
    recorder = get_recorder()
    model = kwargs.get("model", "unknown")
    
    with recorder.start_span(tool_name="anthropic.messages.create_async", model=model) as span:
        try:
            response = await _original_acreate(self, *args, **kwargs)
            
            if kwargs.get("stream", False):
                pass
            else:
                _extract_usage(response, span)
                
            return response
        except Exception as e:
            raise
