"""Call ViewSelectionAdvisor.advise()."""

from ViewSelectionAdvisor import ViewSelectionAdvisor

if __name__ == "__main__":

    print()
    print("Welcome to ViewSelectionAdvisor!")
    print("This tool helps dbt users make informed decisions about view materialization.")

    view_selection_advisor = ViewSelectionAdvisor(
        n_mater_in_config=2
    )

    print()
    print("Analyzing your DAG to provide the best advice...")
    print()

    best_config = view_selection_advisor.advise()

    print()
    print("Our advice is to materialize the following models: ")
    print(best_config)
    print()
