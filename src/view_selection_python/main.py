"""Call ViewSelectionAdvisor.advise()."""

from .ViewSelectionAdvisor import ViewSelectionAdvisor
from .CLI import CLI
from .OutputPrinter import OutputPrinter


def run():
    print()
    print("Welcome to ViewSelectionAdvisor!")
    print("This tool helps dbt users make informed decisions about view materialization.")

    cli = CLI()

    view_selection_advisor = ViewSelectionAdvisor(
        n_mater_in_config=cli.get_max_materializations()
    )

    print()
    print("Analyzing your DAG to provide the best advice...")
    print()

    results = view_selection_advisor.advise()

    print()
    print("Our analysis yielded the following results: ")
    print()

    output_printer = OutputPrinter(
        results=results
    )
    output_printer.print_output()

    print()
