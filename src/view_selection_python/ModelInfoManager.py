from PostgresHandler import PostgresHandler
from CostEstimatorSinglePlan import CostEstimatorSinglePlan
from SQLRewriter import SQLRewriter
from ast import literal_eval
from typing import List, Tuple, Dict, KeysView


class ModelInfoManager:
    def __init__(self, postgres_handler: PostgresHandler):
        self.postgres_handler = postgres_handler

        self.model_info_dict = {}
        self._fill_dict()

    def _create_skeleton_from_models_and_code(self):
        """
        Create skeleton of dict:
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
            self.model_info_dict[model_id] = {'code': compiled_code, 'referenced_by': []}

    def _fill_depends_on(self, upstream_model: str, downstream_models: List[str]):
        # TODO make this happen here
        pass

    def _update_referenced_by(self):
        # TODO make this happen here, and remove that action from the other recursive stuff happening
        pass

    def _include_info_model_dependencies(self):
        """
        Add model dependencies and compiled_code_references:
        {
            model_id:
                {
                    code: CODE
                    referenced_by: []
                    depends_on: [model_id, model_id]
                    compiled_code_reference: "db_name"."schema_name"."alias"
                }
        }
        """
        model_dependencies = self.postgres_handler.get_model_dependencies()
        for model_id, dependencies, compiled_code_ref in model_dependencies:
            model_id_dict = self.model_info_dict[model_id]
            model_id_dict['depends_on'] = literal_eval(dependencies)
            model_id_dict['compiled_code_reference'] = compiled_code_ref

    def _rewrite_sql(self):
        """Rewrite the sql of the models using SQLRewriter"""
        sql_rewriter = SQLRewriter(self.model_info_dict, self.postgres_handler.get_destination_nodes())
        sql_rewriter.update_all_sql_code()

    def _retrieve_storage_and_execution_cost(self, model: str) -> Tuple[float, float]:
        """Return the storage and execution cost of a model"""
        explain_friendly_code = self.model_info_dict[model]['code']
        query_plan = self.postgres_handler.get_output_explain(explain_friendly_code)
        return CostEstimatorSinglePlan().estimate_costs(query_plan)

    def _add_costs_per_model(self):
        """
        Add storage and execution cost to the info dict:
        {
            model_id:
                {
                    storage_cost: storage_cost
                    execution_cost: execution_cost
                }
        }
        """
        for model, info in self.model_info_dict.items():
            storage_cost, execution_cost = self._retrieve_storage_and_execution_cost(model)
            info['storage_cost'] = storage_cost
            info['execution_cost'] = execution_cost

    def _fill_dict(self):
        """Fill the dict with all relevant info"""
        self._create_skeleton_from_models_and_code()
        self._include_info_model_dependencies()
        self._rewrite_sql()
        self._add_costs_per_model()

    def get_model_info_dict(self) -> Dict[str, Dict]:
        """Return the model info dictionary"""
        return self.model_info_dict

    def get_all_models_ids(self) -> KeysView[str]:
        """
        Return all the models observed in the dbt project under investigation
        """
        return self.model_info_dict.keys()

    def get_list_of_destination_nodes(self) -> List[str]:
        """Transform List[Tuple[str]] to List[str]"""
        postgres_output = self.postgres_handler.get_destination_nodes()
        return [model for model_tuple in postgres_output for model in model_tuple]

    def get_all_intermediate_models(self) -> List[str]:
        """Return all intermediate nodes/models"""
        destination_nodes = self.get_list_of_destination_nodes()
        all_models = self.get_all_models_ids()
        return [model for model in all_models if model not in destination_nodes]
