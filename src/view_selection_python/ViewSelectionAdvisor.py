"""ViewSelectionAdvisor class."""

from math import inf
from typing import Deque, Tuple, List

from collections import deque
from .ConfigCostEstimator import ConfigCostEstimator
from .ConfigurationGenerator import MaterializationConfigurationGenerator
from .CwdChecker import CwdChecker
from .ModelInfoManager import ModelInfoManager
from .PostgresHandler import PostgresHandler
from ruamel.yaml.comments import CommentedMap
from .ProfilesScraper import ProfilesScraper
from .DbtProjectScraper import DbtProjectScraper
from tqdm import tqdm
from .CLI import CLI


class ViewSelectionAdvisor:
    """The ViewSelectionAdvisor class.

    This class compares all possible configurations, and picks
    the one with the lowest expected cost.
    """

    def __init__(self, n_mater_in_config: int = 2):
        """Initialize, do checks to the environment, and create necessary objects."""
        self.n_mater_in_config = n_mater_in_config
        self.cwd_checker = CwdChecker()
        self.dbt_project_scraper = None
        self.profiles_scraper = None
        self.postgres_handler = None
        self.model_info_manager = None
        self.config_cost_estimator = None
        self._create_necessary_objects()

    def _create_necessary_objects(self):
        """Create objects necessary for providing the view selection advise."""
        self._create_dbt_project_scraper()
        self._create_profiles_scraper()
        self._create_postgres_handler()
        self._create_model_info_manager()
        self._create_config_cost_estimator()

    def _create_dbt_project_scraper(self):
        """Create an instance of DbtProjectScraper which will read contents of dbt_project.yml."""
        dbt_project_path = self.cwd_checker.get_dbt_project_path()
        self.dbt_project_scraper = DbtProjectScraper(filepath=dbt_project_path)

    def _get_profile_name(self) -> str:
        """Return the profile which contains the relevant db credentials."""
        # If the user manually specified a profile through cli, use that one
        cli = CLI()
        cli_profile = cli.get_profile()

        if cli_profile:
            return cli_profile

        # If no specified profile in cli, use the profile specified in dbt_project.yml
        else:
            return self.dbt_project_scraper.get_profile()

    def _create_profiles_scraper(self):
        """Create an instance of ProfilesScraper which will read contents of profiles.yml."""
        profiles_yml_path = self.cwd_checker.get_profiles_path()
        profile_name = self._get_profile_name()
        self.profiles_scraper = ProfilesScraper(
            filepath=profiles_yml_path,
            profile_name=profile_name
        )

    def _obtain_db_credentials(self) -> CommentedMap:
        """Return the db credentials of the DB schema.

        This is the schema where the relevant tables from the dbt
        part of the ViewSelectionTool are stored
        """
        return self.profiles_scraper.get_db_creds(
            schema_appendix=self.dbt_project_scraper.get_schema_appendix(
                profile='view_selection_tool'
            )
        )

    def _create_postgres_handler(self):
        """Create an instance of PostgresHandler which will communicate with the DB."""
        db_creds = self._obtain_db_credentials()
        self.postgres_handler = PostgresHandler(db_creds=db_creds)

    def _create_model_info_manager(self):
        """Create an instance of ModelInfoManager.

        This instance which will contain all potentially relevant info on the models.
        """
        self.model_info_manager = ModelInfoManager(
            postgres_handler=self.postgres_handler
        )

    def _create_config_cost_estimator(self):
        """Create an instance of ConfigCostEstimator.

        This instance which will calculate the cost for each possible configuration.
        """
        self.config_cost_estimator = ConfigCostEstimator(
            models_info_dict=self.model_info_manager.get_model_info_dict(),
            destination_nodes=self.model_info_manager.get_list_of_destination_nodes(),
        )

    def _get_configs_to_check(self) -> Deque[None | Tuple[str]]:
        """Create a deque of configurations to check the cost for."""
        config_list_generator = MaterializationConfigurationGenerator(
            all_intermediate_models=self.model_info_manager.get_all_intermediate_models(),  # noqa E501
            max_materializations=self.n_mater_in_config
        )
        return config_list_generator.get_all_possible_configurations()

    def advise(self) -> Deque:
        """
        Analyzes possible configurations and returns those that fit within the storage bounds.

        This method iterates over all potential configurations, estimates their total cost
        and storage requirements, and stores those configurations that fit within the available
        storage space.

        Returns:
            Deque: A deque of dictionaries, each containing a valid configuration and its
            associated total configuration cost.
        """
        configs_to_check = self._get_configs_to_check()

        storage_bound = self.postgres_handler.get_storage_space_left()

        results = deque()

        for config in tqdm(configs_to_check):

            total_config_cost, total_storage_cost = (
                self.config_cost_estimator.estimate_cost_of_configuration(config)
            )

            # If won't fit don't use
            if total_storage_cost < storage_bound:

                # Store in results
                results.append({
                    'config': config,
                    'total_config_cost': total_config_cost
                })

        return results
