from .YamlScraper import YamlScraper
from .Exceptions.errors import NO_SCHEMA_ERROR


class DbtProjectScraper(YamlScraper):
    """
    A class to scrape and process dbt_project.yml files.

    Attributes:
        filepath (str): The path to the YAML file to be scraped.
    """

    def __init__(self, filepath: str):
        """
        Initializes a DbtProjectScraper instance with the provided filepath.

        Args:
            filepath (str): The path to the dbt project's YAML file.
        """
        super().__init__(filepath)

    def get_name(self) -> str:
        """
        Gets the name of the dbt project from the YAML contents.

        Returns:
            str: The name of the dbt project.
        """
        return self.contents['name']

    def get_schema_appendix(self, profile: str) -> str:
        """
        Gets the schema appendix for a specified profile from the YAML contents.

        Args:
            profile (str): The profile for which to retrieve the schema appendix.

        Returns:
            str: The schema appendix associated with the specified profile.

        Raises:
            ValueError: If the profile does not have an associated schema appendix in the YAML contents.
        """
        try:
            return self.contents['models'][profile]['+schema']
        except KeyError:
            raise ValueError(
                NO_SCHEMA_ERROR.replace('REPLACE_WITH_PROFILE', profile)
            )

    def get_profile(self) -> str:
        """
        Gets the profile used in the dbt project from the YAML contents.

        Returns:
            str: The profile used in the dbt project.
        """
        return self.contents['profile']
