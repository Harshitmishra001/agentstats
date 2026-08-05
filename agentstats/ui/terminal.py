from rich.console import Console
from rich.table import Table
from ..recorder import get_recorder

def print_report():
    """Print a terminal summary of the recorded spans."""
    recorder = get_recorder()
    spans = recorder.get_completed_spans()
    
    if not spans:
        print("No agentstats recorded yet.")
        return

    console = Console()
    table = Table(title="AgentStats Run Summary")

    table.add_column("Tool / Model", style="cyan", no_wrap=True)
    table.add_column("Status", style="bold")
    table.add_column("Latency (s)", justify="right")
    table.add_column("Tokens (In/Out)", justify="right")
    table.add_column("Error", style="red")

    total_latency = 0.0
    total_in = 0
    total_out = 0
    failures = 0

    for span in spans:
        latency = span.end_ts - span.start_ts if span.end_ts else 0.0
        total_latency += latency
        total_in += span.tokens_in
        total_out += span.tokens_out
        
        if span.status == "error":
            failures += 1
            status_str = "[red]Error[/red]"
        elif span.status == "success":
            status_str = "[green]Success[/green]"
        else:
            status_str = "[yellow]Running[/yellow]"

        error_msg = span.raw_error if span.raw_error else ""
        if len(error_msg) > 30:
            error_msg = error_msg[:27] + "..."

        name = f"{span.tool_name}\n({span.model})" if span.model else span.tool_name

        table.add_row(
            name,
            status_str,
            f"{latency:.2f}",
            f"{span.tokens_in} / {span.tokens_out}",
            error_msg
        )

    console.print(table)
    
    # Summary footer
    console.print(f"\nTotal Calls: {len(spans)}")
    console.print(f"Failures:    [red]{failures}[/red]")
    console.print(f"Total Time:  {total_latency:.2f}s")
    console.print(f"Total Tokens: {total_in + total_out} ({total_in} in, {total_out} out)\n")
