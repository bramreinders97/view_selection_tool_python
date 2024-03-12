"""Call ViewSelectionAdvisor.advise()."""

from ViewSelectionAdvisor import ViewSelectionAdvisor

if __name__ == "__main__":

    view_selection_advisor = ViewSelectionAdvisor()
    best_config = view_selection_advisor.advise()

    print(best_config)
