from typing import List, Tuple, Deque
from collections import deque
import itertools


class MaterializationConfigurationGenerator:
    def __init__(self, all_intermediate_models: List[str], max_materializations: int = 2):
        self.all_intermediate_models = all_intermediate_models
        self.max_materializations = max_materializations

    def get_all_possible_configurations(self) -> Deque[None | Tuple[str]]:
        """Return a deque of all possible materialization configurations"""
        materialization_configs = deque([None])

        # Create deque of all possible materialization configurations
        for num_materializations in range(self.max_materializations, 0, -1):
            materialization_configs.extend(
                itertools.combinations(
                    self.all_intermediate_models, num_materializations
                )
            )

        return materialization_configs
