from typing import Tuple, Dict

fudge_factors_lists = [
            [0.01, 0.25, 0.50, 0.70, 0.80, 0.90],
            [0.25, 0.60, 0.60, 0.80, 0.90, 0.95]
        ]


def _get_fudge_list_index_to_use(n_outgoing_edges: int) -> int:
    """
    Return the index which will be used to obtain the correct fudge_factor_list from
    `fudge_factors_lists`

    If a materialized node has one outgoing edge, we use [0.25, 0.60, 0.60, 0.80, 0.90, 0.95]
    if a materialized node has more than 1 outgoing edges, we use [0.01, 0.25, 0.50, 0.70, 0.80, 0.90]
    """
    return 0 if n_outgoing_edges >= 2 else 1


def _get_next_fudge_factor(fudge_list_index: int, fudge_factor_index: int):
    """
    Return the fudge factor of a model. If a model is too far away from the materialized model,
    the fudge factor is 1
    """
    try:
        fudge_factor_list = fudge_factors_lists[fudge_list_index]
        next_fudge_factor = fudge_factor_list[fudge_factor_index]
        return next_fudge_factor
    except IndexError:
        return 1


class FudgeFactorCalculator:
    """
    This class creates a dict of the form
    {
        model_id: fudge_factor
    }

    The fudge factor a model receives depends on
     - the amount of nodes it lies from a materialized model
     - the number of outgoing edges that materialized model has
    """
    def __init__(self, config: None | Tuple[str], models_info_dict: Dict[str, Dict]):
        self.config = config
        self.models_info_dict = models_info_dict
        self.fudge_factor_dict = self._get_dict_template()

    def _get_dict_template(self):
        """
        Create template for dictionary to keep track of fudge factors of the form
        {
            model_id: fudge_factor
        }
        """
        return {model: 1 for model in self.models_info_dict.keys()}

    def _get_number_downstream_references_of_model(self, model: str) -> int:
        """Return the number of outgoing edges of a model"""
        all_downstream_refs = self.models_info_dict[model]['referenced_by']
        return len(all_downstream_refs)

    def _update_fudge_factor(self, model: str, fudge_list_index: int, fudge_factor_index: int):
        """
        Recursively update the fudge factors of all models downstream of a materialized model.
        """
        self.fudge_factor_dict[model] = _get_next_fudge_factor(
            fudge_list_index=fudge_list_index,
            fudge_factor_index=fudge_factor_index
        )

        # Go to next downstream model, do same recursively
        downstream_models = self.models_info_dict[model]['referenced_by']

        for downstream_model in downstream_models:
            self._update_fudge_factor(
                model=downstream_model,
                fudge_list_index=fudge_list_index,
                fudge_factor_index=fudge_factor_index+1
            )

    def _core_logic(self):
        """
        for all materialized models x,
        loop over the models downstream of x and update their fudge factor
        """
        for materialized_model in self.config:
            n_downstream_refs = self._get_number_downstream_references_of_model(materialized_model)

            if n_downstream_refs > 0:
                fudge_list_index = _get_fudge_list_index_to_use(
                    n_outgoing_edges=n_downstream_refs
                )

                downstream_models = self.models_info_dict[materialized_model]['referenced_by']

                for downstream_model in downstream_models:
                    self._update_fudge_factor(
                        model=downstream_model,
                        fudge_list_index=fudge_list_index,
                        fudge_factor_index=0
                    )

    def get_fudge_factors(self) -> Dict[str, int]:
        """
        Return dict of the form
        {
            model_id: fudge_factor
        }

        If config is None, there are no materialized intermediate models, so
        no fudge factors are needed -> all models have factor 1
        """
        if self.config is not None:
            self._core_logic()
        return self.fudge_factor_dict
