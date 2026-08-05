from .adapters import patch_all, unpatch_all
from .ui import print_report
from .recorder import get_recorder
from .export import export_json as export

def watch():
    """Auto-instruments available LLM SDKs (OpenAI, Anthropic, etc)."""
    patch_all()

def report(classify=False):
    """Prints the summary report of all tracked agent calls."""
    # classify will be implemented in v2
    print_report()

def clear():
    """Clears all recorded spans."""
    get_recorder().clear()

__all__ = ["watch", "report", "clear", "export"]
