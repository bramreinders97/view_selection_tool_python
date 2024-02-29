from typing import List, Dict, Tuple


def _check_for_subplans(plan: Dict) -> bool:
    """Check if the plan contains subplans."""
    return 'Plans' in plan


def _calculate_cost(expected_rows: float, expected_width: float) -> float:
    """Calculate the cost based on expected rows and width."""
    return expected_rows * expected_width


def _read_plan_contents(plan: Dict) -> Tuple[float, float, List[Dict] | None]:
    """Extract expected rows, width, and subplans from the plan."""
    expected_rows = plan['Plan Rows']
    expected_width = plan['Plan Width']

    subplans = plan['Plans'] if _check_for_subplans(plan) else None

    return expected_rows, expected_width, subplans


def _extract_plan_from_list(list_with_plan: List[Dict]):
    """Extract the plan from a list"""
    return list_with_plan[0]['Plan']


class CostEstimatorSinglePlan:
    """
    This class estimates the cost of a single model.

    This is done by traversing through the entire query plan as obtained by calling
    EXPLAIN in postgres
    """
    def __init__(self):
        self._reset_costs()

    def _reset_costs(self):
        self.storage_cost = 0
        self.creation_cost = 0

    def _update_storage_cost(self, cost: float):
        """Update the storage cost."""
        self.storage_cost += cost

    def _update_creation_cost(self, cost: float):
        """Update the creation cost."""
        self.creation_cost += cost

    def _update_costs(self, cost: float, is_root_of_plan: bool):
        """Update both storage and creation costs, storage cost only if it's the root of the plan."""
        if is_root_of_plan:
            self._update_storage_cost(cost)

        self._update_creation_cost(cost)

    def estimate_costs(self, plan: List[Dict] | Dict, is_root_of_plan: bool = True) -> Tuple[float, float]:
        """
        Estimate costs based on the provided plan, by extracting the E[#rows]
        and the E[width] of each row. Do this recursively over all subplans, to
        get all the relevant costs.
        """
        if is_root_of_plan:
            self._reset_costs()

        if isinstance(plan, List):
            plan = _extract_plan_from_list(plan)

        expected_rows, expected_width, subplans = _read_plan_contents(plan)
        cost = _calculate_cost(expected_rows, expected_width)

        self._update_costs(cost, is_root_of_plan=is_root_of_plan)

        if subplans:
            for subplan in subplans:
                self.estimate_costs(subplan, is_root_of_plan=False)

        return self.storage_cost, self.creation_cost
