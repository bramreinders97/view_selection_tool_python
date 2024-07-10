"""DistanceDict class."""
from typing import Dict, Tuple
from math import inf


class DistanceCalculator:
    """Calculate the distance to the nearest previously materialized model for each model.

    This class computes the distance of each model from the nearest materialized model
    based on the provided configuration and model_info_dict.
    """

    def __init__(self, config: None | Tuple[str], models_info_dict: Dict[str, Dict]):
        """Initialize the class."""
        self.config = config
        self.models_info_dict = models_info_dict
        self.distances_dict = self._get_dict_template()

    def _get_dict_template(self) -> Dict[str, float]:
        """Create a template for the distance's dictionary.

        This dictionary initializes the distance to infinity for each model.
        """
        return {model: inf for model in self.models_info_dict.keys()}

    def _get_number_downstream_references_of_model(self, model: str) -> int:
        """Return the number of outgoing edges of a model."""
        all_downstream_refs = self.models_info_dict[model]["referenced_by"]
        return len(all_downstream_refs)

    def _update_distance(
        self, model: str, new_distance: int
    ):
        """Recursively update the distances of all models.
        """
        curr_dist = self.distances_dict[model]
        self.distances_dict[model] = min(curr_dist, new_distance)

        # Go to next downstream model, do same recursively
        downstream_models = self.models_info_dict[model]["referenced_by"]

        for downstream_model in downstream_models:
            self._update_distance(
                model=downstream_model,
                new_distance=new_distance+1
            )

    def _core_logic(self):
        """Update distances for all models.

        For all materialized models x,
        Loop over the models downstream of x and update their distance
        """
        for materialized_model in self.config:
            n_downstream_refs = self._get_number_downstream_references_of_model(materialized_model)

            if n_downstream_refs > 0:
                downstream_models = self.models_info_dict[materialized_model]["referenced_by"]

                for downstream_model in downstream_models:
                    self._update_distance(
                        model=downstream_model,
                        new_distance=1
                    )

    def get_distances(self) -> Dict[str, int | float]:
        """Return the dict of distances.

        This dict has the following form:
        {
            model_id: distance
        }

        If config is None, there are no materialized intermediate models,
        all models have distance infinity.
        """
        if self.config is not None:
            self._core_logic()
        return self.distances_dict
