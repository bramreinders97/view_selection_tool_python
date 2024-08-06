"""ConfigCostEstimator class."""

from typing import Dict, List, Tuple

from FudgeFactorCalculator import FudgeFactorCalculator


class ConfigCostEstimator:
    """This class is responsible for estimating the cost of a given configuration.

    This is done by summing the cost = storage_cost = (creation_cost * fudge_factor)
    for each model to be materialized.

    A single instance of this class can estimate the cost of
        - multiple different materialization configurations (specified by `config` in
          estimate_cost_of_configuration())
        - from a single DAG (specified by models_info_dict` and `destination_nodes` in
          __init__())
    """

    def __init__(self, models_info_dict: Dict[str, Dict], destination_nodes: List[str]):
        """Initialize ConfigCostEstimator class."""
        self.models_info_dict = models_info_dict
        self.destination_nodes = destination_nodes
        self.current_config_fudge_factors = None

    def _get_fudge_factors_current_config(
        self, config: None | Tuple[str]
    ) -> Dict[str, int]:
        """Return a dict with key `model_id` and value `fudge_factor`."""
        fudge_calculator = FudgeFactorCalculator(
            config=config, models_info_dict=self.models_info_dict
        )
        return fudge_calculator.get_fudge_factors()

    def _get_storage_cost(self, model: str) -> float:
        """Return the storage cost of `model`."""
        return self.models_info_dict[model]["storage_cost"]

    def _get_creation_cost(self, model: str) -> float:
        """Return the creation cost of `model`."""
        return self.models_info_dict[model]["creation_cost"]

    def _get_fudge_factor(self, model: str) -> float:
        """Return the fudge factor of a given model under the current configuration."""
        return self.current_config_fudge_factors[model]

    def _calc_execution_cost(self, model: str) -> float:
        """Return the execution cost of a node.

        The execution cost is calculated using the formula:
            execution_cost =  storage_cost + (creation_cost * fudge_factor)
        """
        storage_cost = self._get_storage_cost(model)
        creation_cost = self._get_creation_cost(model)
        fudge_factor = self._get_fudge_factor(model)
        return storage_cost + (creation_cost * fudge_factor)


    def _calc_total_cost(self, model: str) -> float:
        """Return the total cost of a node.

        The total cost is calculated using the formula:
            total_cost = execution_cost + maintenance_cost
        """
        execution_cost = self._calc_execution_cost(model)
        return execution_cost

    def _get_costs_single_node(self, model: str) -> Tuple[float, float]:
        """Return the total cost and storage cost of a single node."""
        total_cost = self._calc_total_cost(model)
        storage_cost = self._get_storage_cost(model)
        return total_cost, storage_cost

    def _calc_cost_model_set(
        self, model_set: Tuple[str] | List[str]
    ) -> Tuple[float, float]:
        """Calculate the creation- and storage cots of all models in a set of models.

        This is done by summing the individual costs
        """
        total_cost = 0
        storage_cost = 0

        for model in model_set:
            total_cost_model, storage_cost_model = self._get_costs_single_node(model)
            total_cost += total_cost_model
            storage_cost += storage_cost_model

        return total_cost, storage_cost

    def _calc_cost_intermediate_models(self, config: Tuple[str]) -> Tuple[float, float]:
        """Return the total costs of all the intermediate models."""
        return self._calc_cost_model_set(model_set=config)

    def _calc_cost_destination_nodes(self) -> Tuple[float, float]:
        """Return the total costs of all the destination models."""
        return self._calc_cost_model_set(model_set=self.destination_nodes)

    def estimate_cost_of_configuration(
        self, config: None | Tuple[str]
    ) -> Tuple[float, float]:
        """Estimate the total costs of the given configuration."""
        # Set fudge factors for current configuration
        self.current_config_fudge_factors = self._get_fudge_factors_current_config(
            config=config
        )

        # Calculate cost intermediate models
        if config is not None:
            total_cost_intermediate, storage_cost_intermediate = (
                self._calc_cost_intermediate_models(config)
            )
        else:
            total_cost_intermediate, storage_cost_intermediate = 0, 0

        # Calculate cost of the destination models
        total_cost_destination, storage_cost_destination = (
            self._calc_cost_destination_nodes()
        )

        # Sum total costs
        total_cost = total_cost_intermediate + total_cost_destination
        total_storage_cost = storage_cost_intermediate + storage_cost_destination

        return total_cost, total_storage_cost
