from .YamlScraper import YamlScraper
from ruamel.yaml.comments import CommentedMap
from .CLI import CLI


def _get_cli_specified_target() -> str | None:
    """
    Retrieves the target specified via the command-line interface (CLI).

    Returns:
        str | None: The target specified by the CLI, or None if no target is specified.
    """
    cli = CLI()
    return cli.get_target()


class ProfilesScraper(YamlScraper):
    """
    A class to scrape and process profile.yml files.
    """

    def __init__(self, filepath: str, profile_name: str):
        """
        Initializes a ProfilesScraper instance with the provided filepath and profile name.

        Args:
            filepath (str): The path to the profiles YAML file.
            profile_name (str): The name of the profile to be processed.
        """
        super().__init__(filepath)
        self.profile_name = profile_name
        self.profile_content = self._get_profile_content()
        self.profile_outputs = self._get_profile_outputs()
        self.cli_specified_target = _get_cli_specified_target()

    def _get_profile_content(self) -> CommentedMap:
        """
        Retrieves the content of the specified profile from the YAML file.

        Returns:
            CommentedMap: The content of the specified profile.
        """
        return self.contents[self.profile_name]

    def _get_profile_outputs(self) -> CommentedMap:
        """
        Retrieves the outputs section of the specified profile.

        Returns:
            CommentedMap: The outputs section of the specified profile.
        """
        return self._get_profile_content()['outputs']

    def _get_target(self) -> str:
        """
        Determines the target to use for the dbt profile.

        Returns:
            str: The determined target.
        """
        # Check if the user manually specified a target through the CLI
        if self.cli_specified_target:
            return self.cli_specified_target

        # Check if a target is specified in profiles.yml
        specified_target = self.profile_content.get('target', None)

        # If a target is specified, use it
        if specified_target:
            return specified_target

        # If no target is specified, there will only be one target available,
        # so use that one
        else:
            return list(self.profile_outputs.keys())[0]

    def get_db_creds(self, schema_appendix: str) -> CommentedMap:
        """
        Retrieves the database credentials for the current profile,
        appending the given schema appendix to the schema variable.

        Args:
            schema_appendix (str): The schema appendix to append to the database schema.

        Returns:
            CommentedMap: The database credentials with the schema appendix added.
        """
        target = self._get_target()

        db_creds = self.profile_outputs[target]

        # append the schema appendix
        db_creds['schema'] = f"{db_creds['schema']}_{schema_appendix}"

        return db_creds
