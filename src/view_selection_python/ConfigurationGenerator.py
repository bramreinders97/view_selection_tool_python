"""MaterializationConfigurationGenerator class."""

import itertools
from collections import deque
from typing import Deque, List, Tuple


class MaterializationConfigurationGenerator:
    """MaterializationConfigurationGenerator class.

    This class creates a deque of all possible materialization configurations
    """

    def __init__(
        self, all_intermediate_models: List[str], max_materializations: int = 2
    ):
        """Initialize the class."""
        self.all_intermediate_models = all_intermediate_models
        self.max_materializations = max_materializations

    def get_all_possible_configurations(self) -> Deque[None | Tuple[str]]:
        """Return a deque of all possible materialization configurations."""
        materialization_configs = deque([None])

        # Create deque of all possible materialization configurations
        for num_materializations in range(self.max_materializations, 0, -1):
            materialization_configs.extend(
                itertools.combinations(
                    self.all_intermediate_models, num_materializations
                )
            )

        return materialization_configs
