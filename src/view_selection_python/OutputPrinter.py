from typing import Dict, List, Deque
from tabulate import tabulate
from .CLI import CLI


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
        percentage_diff = ((config_cost / self.default_cost) - 1) * 100
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

    @staticmethod
    def _get_number_of_configs_to_print() -> int:
        """
        Retrieves the number of configurations to display from the command-line interface.

        This method initializes a CLI instance and fetches the number of top configurations
        that the user wants to display.

        Returns:
            int: The number of configurations to print.
        """
        cli = CLI()
        return cli.get_top_x()

    def print_output(self):
        """
        Prints a table of configurations and their percentage difference from the default cost.

        This method retrieves the number of configurations to display, formats the data accordingly,
        and then prints the table with two columns: 'Config' and '% Difference with default'.

        The table only includes the top configurations as specified by the user.

        """
        # Get number of configs to print
        top_x = self._get_number_of_configs_to_print()

        # Extracting data for the table
        table_data = [
            (self._format_config_col(result['config']), self._format_difference_cell(result['total_config_cost']))
            for result in self.results_sorted[:top_x]
        ]

        # Printing the table
        print(tabulate(table_data, headers=['Config', '% Difference with default'], tablefmt='pretty'))
