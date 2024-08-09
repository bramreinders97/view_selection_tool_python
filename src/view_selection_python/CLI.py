"""
CLI class.
"""

import argparse
import os


def _get_args() -> argparse.Namespace:
    """
    This function is responsible for parsing the command-line arguments provided by the user when running the View Selection Tool.
    It uses the argparse module to define and parse these arguments.

    The function defines three command-line arguments:
    1. max_materializations: This argument is used to specify the maximum number of models to materialize. It is an integer and its default value is 2.
    2. profile: This argument is used to select the profile to use. It is a string.
    3. target: This argument is used to select the target profile to use. It is a string.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="View Selection Tool",
        description="Advice on which models to materialize in dbt",
    )

    # Define the max_materializations argument
    parser.add_argument(
        "-mm",
        "--max_materializations",
        type=int,
        default=2,
        help="Set the maximum number of models to materialize. Higher values provide more options but may "
             "increase runtime. Default is 2."
    )

    # Define the profile argument
    parser.add_argument(
        "-p",
        "--profile",
        type=str,
        help="Select the profile to use"
    )

    # Define the target argument
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        help="Select the target profile to use"
    )

    # Define top-x argument
    parser.add_argument(
        "-x",
        "--top_x",
        type=int,
        default=10,
        help="Select the top x configurations to print in the terminal. Default is 10."
    )

    # Parse the command-line arguments and return the result
    return parser.parse_args()


class CLI:
    """
    Command-Line Interface (CLI) for the View Selection Tool.

    The CLI class is responsible for handling the parsed command-line arguments and
    providing methods to access them. It supports retrieving the root working directory
    and the maximum number of models to materialize as specified by the user.
    """

    def __init__(self):
        """
        Initializes the CLI instance.

        This constructor parses the command-line arguments and stores them as attributes
        for later use in the instance methods.
        """
        self.args = _get_args()

    def get_max_materializations(self) -> int:
        """
        Retrieve the maximum number of models to materialize from the CLI arguments.

        Returns:
            int: The maximum number of models to materialize, as specified by the user.
            The default value is 2 if no argument is provided.
        """
        return self.args.max_materializations

    def get_profile(self) -> str | None:
        """
        Retrieve the profile specified in the CLI arguments.

        Returns:
            str | None: The profile to use as specified in the command-line arguments.
            Returns None if no profile is specified.
        """
        return self.args.profile

    def get_target(self) -> str | None:
        """
        Retrieve the target profile specified in the CLI arguments.

        Returns:
            str | None: The target profile to use as specified in the command-line arguments.
            Returns None if no target profile is specified.
        """
        return self.args.target

    def get_top_x(self) -> int:
        """
        Retrieve the amount of configurations to print in the terminal.

        Returns:
            int: The top x configurations to print in the terminal, as specified by the user.
            The default value is 10 if no argument is provided.
        """
        return self.args.top_x
