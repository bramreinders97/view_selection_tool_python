from CwdChecker import CwdChecker
from YamlScraper import YamlScraper
from PostgresHandler import PostgresHandler
from ModelInfoManager import ModelInfoManager
from ConfigCostEstimator import ConfigCostEstimator
from ConfigurationGenerator import MaterializationConfigurationGenerator
from ruamel.yaml.comments import CommentedMap
from math import inf
from typing import Deque, Tuple


class ViewSelectionAdvisor:
    def __init__(self):
        self.cwd_checker = CwdChecker()
        self.postgres_handler = None
        self.model_info_manager = None
        self.config_cost_estimator = None

        self._do_environment_checks()
        self._create_necessary_objects()

    def _create_necessary_objects(self):
        """
        Create objects necessary for providing the view selection advise
        """
        self._create_postgres_handler()
        self._create_model_info_manager()
        self._create_config_cost_estimator()

    def _do_environment_checks(self):
        """
        Do necessary checks to verify if the user is calling our tool from a correct
        working directory
        """
        self.cwd_checker.do_all_checks()

    def _obtain_profiles_path(self) -> str:
        """Return the path of the profiles.yml file of the user's project"""
        return self.cwd_checker.get_profiles_path()

    def _obtain_db_credentials(self) -> CommentedMap:
        """
        Return the db credentials of the DB schema where the relevant tables from the dbt
        part of the ViewSelectionTool are stored
        """
        profiles_yml_path = self._obtain_profiles_path()
        yml_scraper = YamlScraper(profiles_yml_path)
        db_creds = yml_scraper.extract_db_creds()
        return db_creds

    def _create_postgres_handler(self):
        """
        Create an instance of PostgresHandler which will communicate with the DB
        """
        db_creds = self._obtain_db_credentials()
        self.postgres_handler = PostgresHandler(
            db_creds=db_creds
        )

    def _create_model_info_manager(self):
        """
        Create an instance of ModelInfoManager which will contain all potentially
        relevant info on the models
        """
        self.model_info_manager = ModelInfoManager(
            postgres_handler=self.postgres_handler
        )

    def _create_config_cost_estimator(self):
        """
        Create an instance of ConfigCostEstimator which will calculate the cost for each
        possible configuration
        """
        self.config_cost_estimator = ConfigCostEstimator(
            models_info_dict=self.model_info_manager.get_model_info_dict(),
            destination_nodes=self.model_info_manager.get_list_of_destination_nodes()
        )

    def _get_configs_to_check(self) -> Deque[None | Tuple[str]]:
        """
        Create a deque of configurations to check the cost for
        """
        config_list_generator = MaterializationConfigurationGenerator(
            all_intermediate_models=self.model_info_manager.get_all_intermediate_models()
        )
        return config_list_generator.get_all_possible_configurations()

    def advise(self):
        """
        Find and return the best configuration

        This is done by looping over all possible configuration and keeping track of
        which configuration result in the lowest cost.

        When checking a configuration, also make sure it fits within the storage bound
        """
        configs_to_check = self._get_configs_to_check()

        minimal_cost = inf
        best_config = None

        storage_bound = self.postgres_handler.get_storage_space_left()

        for config in configs_to_check:
            total_config_cost, total_storage_cost = self.config_cost_estimator.estimate_cost_of_configuration(config)
            if (
                    total_config_cost < minimal_cost
                    and
                    total_storage_cost < storage_bound
            ):
                minimal_cost = total_config_cost
                best_config = config

        return best_config
