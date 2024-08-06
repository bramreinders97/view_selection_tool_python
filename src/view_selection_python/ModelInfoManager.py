"""ModelInfoManager class."""

from ast import literal_eval
from typing import Dict, KeysView, List, Tuple

from .CostEstimatorSinglePlan import CostEstimatorSinglePlan
from .PostgresHandler import PostgresHandler
from .SQLRewriter import SQLRewriter


def _fill_depends_on(downstream_model_info: Dict, dependencies: List[str]):
    downstream_model_info["depends_on"] = dependencies


def _fill_in_compiled_code_ref(downstream_model_info: Dict, compiled_code_ref: str):
    downstream_model_info["compiled_code_reference"] = compiled_code_ref


class ModelInfoManager:
    """Class that deals with all relevant info on the models in the DAG.

    this results in a dictionary of the form:
    {
        model_id:
            {
                code: CODE
                referenced_by: [downstream_model_id]
                depends_on: [upstream_model_id]
                compiled_code_reference: "db_name"."schema_name"."alias"
                storage_cost: storage_cost
                creation_cost: creation_cost
                maintenance_fraction: maintenance_fraction
            }
    }
    """

    def __init__(self, postgres_handler: PostgresHandler):
        """Initialize the class, fill the dict with all relevant info."""
        self.postgres_handler = postgres_handler
        self.model_info_dict = {}
        self._fill_dict()

    def _create_skeleton_from_models_and_code(self):
        """Create skeleton of dict.

        This results in the following addition to the dict:
        {
            model_id:
                {
                    code: CODE
                    referenced_by: []
                }
        }
        """
        models_and_code = self.postgres_handler.get_all_models_and_code()
        for model_id, compiled_code in models_and_code:
            self.model_info_dict[model_id] = {
                "code": compiled_code,
                "referenced_by": [],
            }

    def _update_referenced_by(
        self, downstream_model_id: str, upstream_model_ids: List[str]
    ):
        """Add references to downstream models in the dict.

        This results in the following addition to the dict:
        {
            upstream_model_id:
                {
                    referenced_by: [downstream_model_id]
                }
        }
        """
        for upstream_model_id in upstream_model_ids:

            # If the upstream node is a source node, we don't have to store anything,
            # Considering that we don't include any info about source nodes in the
            # info dict
            current_node_is_a_model = upstream_model_id in self.model_info_dict
            if current_node_is_a_model:

                # If the dependency under investigation is recorded already,
                # we do not have to record it again
                currently_known_references = self.model_info_dict[upstream_model_id][
                    "referenced_by"
                ]
                if downstream_model_id not in currently_known_references:
                    currently_known_references.append(downstream_model_id)

    def _include_info_model_dependencies(self):
        """Add model dependencies and compiled_code_references.

        This results in the following addition to the dict:
        {
            model_id:
                {
                    referenced_by: []
                    depends_on: [upstream_model_id]
                    compiled_code_reference: "db_name"."schema_name"."alias"
                }
        }
        """
        model_dependencies = self.postgres_handler.get_model_dependencies()
        for model_id, dependencies_str, compiled_code_ref in model_dependencies:
            model_id_dict = self.model_info_dict[model_id]
            dependencies_list = literal_eval(dependencies_str)

            self._update_referenced_by(
                downstream_model_id=model_id, upstream_model_ids=dependencies_list
            )

            _fill_depends_on(
                downstream_model_info=model_id_dict, dependencies=dependencies_list
            )

            _fill_in_compiled_code_ref(
                downstream_model_info=model_id_dict, compiled_code_ref=compiled_code_ref
            )

    def _rewrite_sql(self):
        """Rewrite the sql of the models using SQLRewriter."""
        sql_rewriter = SQLRewriter(
            self.model_info_dict, self.postgres_handler.get_destination_nodes()
        )
        sql_rewriter.update_all_sql_code()

    def _retrieve_storage_and_creation_cost(self, model: str) -> Tuple[float, float]:
        """Return the storage and creation cost of a model."""
        explain_friendly_code = self.model_info_dict[model]["code"]
        query_plan = self.postgres_handler.get_output_explain(explain_friendly_code)
        return CostEstimatorSinglePlan().estimate_costs(query_plan)

    def _add_costs_per_model(self):
        """Add storage and creation cost to the info dict.

        This results in the following addition to the dict:
        {
            model_id:
                {
                    storage_cost: storage_cost
                    creation_cost: creation_cost
                }
        }
        """
        for model, info in self.model_info_dict.items():
            storage_cost, creation_cost = self._retrieve_storage_and_creation_cost(
                model
            )
            info["storage_cost"] = storage_cost
            info["creation_cost"] = creation_cost

    def _retrieve_maintenance_fractions(self) -> List[Tuple[str]]:
        """Return all maintenance fractions as obtained from the DB."""
        return self.postgres_handler.get_maintenance_fractions()

    def _fill_with_default_mf(self):
        """Fill dict with default maintenance fraction values (=1).

        This results in the following addition to the dict:
        {
            model_id:
                {
                    maintenance_fraction: 1
                }
        }
        """
        for _, info in self.model_info_dict.items():
            info["maintenance_fraction"] = 1

    def _include_maintenance_fractions(self):
        """Add available maintenance fractions to the dict.

        This results in the following addition to the dict:
        {
            model_id:
                {
                    maintenance_fraction: maintenance_fraction
                }
        }
        """
        available_maintenance_fractions = self._retrieve_maintenance_fractions()
        for model, mf in available_maintenance_fractions:
            self.model_info_dict[model]["maintenance_fraction"] = (
                mf if mf is not None else 1
            )

    def _fill_dict(self):
        """Fill the dict with all relevant info."""
        self._create_skeleton_from_models_and_code()
        self._include_info_model_dependencies()
        self._rewrite_sql()
        self._add_costs_per_model()
        self._fill_with_default_mf()
        self._include_maintenance_fractions()

    def get_model_info_dict(self) -> Dict[str, Dict]:
        """Return the model info dictionary."""
        return self.model_info_dict

    def get_all_models_ids(self) -> KeysView[str]:
        """Return all the models observed in the dbt project under investigation."""
        return self.model_info_dict.keys()

    def get_list_of_destination_nodes(self) -> List[str]:
        """Transform List[Tuple[str]] to List[str]."""
        postgres_output = self.postgres_handler.get_destination_nodes()
        return [model for model_tuple in postgres_output for model in model_tuple]

    def get_all_intermediate_models(self) -> List[str]:
        """Return all intermediate nodes/models."""
        destination_nodes = self.get_list_of_destination_nodes()
        all_models = self.get_all_models_ids()
        return [model for model in all_models if model not in destination_nodes]
