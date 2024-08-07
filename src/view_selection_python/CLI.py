"""
CLI class.
"""

import argparse
import os


def _get_args() -> argparse.Namespace:
    """
    Parses command-line arguments for the View Selection Tool.

    The function uses argparse to define and parse the command-line arguments that
    determine the behavior of the tool. It provides options for specifying the root
    working directory and setting the maximum number of models to materialize.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
        It includes the following attributes:
            - root_working_dir (str): The path to use as the root working directory.
            - max_materializations (int): The maximum number of models to materialize,
              with a default value of 2.
    """
    parser = argparse.ArgumentParser(
        prog="View Selection Tool",
        description="Advice on which models to materialize in dbt",
    )

    parser.add_argument(
        "-rwd",
        "--root_working_dir",
        type=str,
        help="The path to use as root working directory",
    )

    parser.add_argument(
        "-mm",
        "--max_materializations",
        type=int,
        default=2,
        help="Set the maximum number of models to materialize. Higher values provide more options but may "
             "increase runtime. Default is 2."
    )

    parser.add_argument(
        "-p",
        "--profile",
        type=str,
        help="Select the profile to use"
    )

    parser.add_argument(
        "-t",
        "--target",
        type=str,
        help="Select the target profile to use"
    )

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

    def get_wd(self) -> str:
        """
        Retrieve the working directory specified in the CLI arguments.

        If no working directory is specified in the command-line arguments, the method
        returns the current working directory.

        Returns:
            str: The normalized path to the root working directory or the current working
            directory if no argument is provided.
        """
        root_wd = self.args.root_working_dir

        if root_wd:
            return os.path.normpath(root_wd)
        else:
            return os.getcwd()

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
