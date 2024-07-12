"""Call ViewSelectionAdvisor.advise()."""

from ViewSelectionAdvisor import ViewSelectionAdvisor
from MAX_MODELS_TO_MATERIALIZE import MAX_MODELS_TO_MATERIALIZE


if __name__ == "__main__":

    print()
    print("Welcome to ViewSelectionAdvisor!")
    print("This tool helps dbt users make informed decisions about view materialization.")

    view_selection_advisor = ViewSelectionAdvisor(
        n_mater_in_config=MAX_MODELS_TO_MATERIALIZE
    )

    print()
    print("Analyzing your DAG to provide the best advice...")
    print()

    best_config = view_selection_advisor.advise()

    print()
    print("Our advice is to materialize the following models: ")
    print(best_config)
    print()
