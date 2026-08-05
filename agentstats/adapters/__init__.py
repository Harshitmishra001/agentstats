# Expose the patch functions
from .openai_compat import patch as patch_openai, unpatch as unpatch_openai
from .anthropic_compat import patch as patch_anthropic, unpatch as unpatch_anthropic

def patch_all():
    patch_openai()
    patch_anthropic()

def unpatch_all():
    unpatch_openai()
    unpatch_anthropic()
