from typing import Dict, List, Deque
from tabulate import tabulate


class OutputPrinter:
    def __init__(self, results: Deque):
        """
        Initializes the OutputPrinter with sorted results and calculates the default cost.

        Args:
            results (Deque): A deque of dictionaries containing configuration results.
        """
        self.results_sorted = self._get_sorted_results(results)
        self.default_cost = self._get_default_cost()

    @staticmethod
    def _get_sorted_results(unsorted_results: Deque) -> List[Dict]:
        """
        Sorts the results by the total configuration cost.

        Args:
            unsorted_results (Deque): A deque of unsorted result. Has a 'config' and a
                                      'total_config_cost' key

        Returns:
            List[Dict]: A sorted list of dictionaries by 'total_config_cost'.
        """
        return sorted(unsorted_results, key=lambda x: x['total_config_cost'])

    def _get_default_cost(self) -> int:
        """
        Retrieves the default cost from the sorted results.

        The default cost is determined by finding the first result where the 'config' key is None,
        since the default configuration contains no materialized models.

        Returns:
            int: The default total configuration cost.
        """
        return next(result['total_config_cost'] for result in self.results_sorted if result['config'] is None)

    def _calc_diff_with_default(self, config_cost: int) -> float:
        """
        Calculates the percentage difference between a given configuration cost and the default cost.

        Args:
            config_cost (int): The total configuration cost to compare with the default cost.

        Returns:
            float: The percentage difference, rounded to three decimal places.
        """
        percentage_diff = (config_cost / self.default_cost) - 1
        return round(percentage_diff, 3)

    def _format_difference_cell(self, config_cost: int) -> str:
        """
        Formats the percentage difference between a given configuration cost and the default cost.

        The formatted string includes a '+' sign for positive differences and is followed by a '%' sign.
        A negative difference already contains a '-' automatically.

        Args:
            config_cost (int): The total configuration cost to compare with the default cost.

        Returns:
            str: A string representing the formatted percentage difference.
        """
        percentage_diff = self._calc_diff_with_default(config_cost)
        return f"{'+' if percentage_diff > 0 else ''}{percentage_diff}%"

    @staticmethod
    def _format_config_col(config: str | None) -> str:
        """
        Formats the configuration value for display in the resulting table.

        If the configuration is None, returns the string 'None'. Otherwise, returns the
        configuration string as-is.

        Args:
            config (str | None): The configuration value to format.

        Returns:
            str: The formatted configuration value.
        """
        return config if config else 'None'

    def print_output(self):
        """
        Prints a table of configurations and their percentage difference from the default cost.

        The table includes two columns: 'Config' and '% Difference with default'.
        """
        # Extracting data for the table
        table_data = [
            (self._format_config_col(result['config']), self._format_difference_cell(result['total_config_cost']))
            for result in self.results_sorted
        ]

        # Printing the table
        print(tabulate(table_data, headers=['Config', '% Difference with default'], tablefmt='pretty'))
