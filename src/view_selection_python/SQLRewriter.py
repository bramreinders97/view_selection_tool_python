"""
This class has the task to reformat the SQL from all models as follows:

 if a model is downstream from model 'x', and references it accordingly in the compiled code:

  - "db_name"."schema_name"."model_x"

we replace that reference with the actual code of model 'x'.

This is done by recursively updating a dict of the form
{
    model_id:
        {
            code: CODE,
            referenced_by: []
            depends_on: [model_id, model_id]
            compiled_code_reference: "db_name"."schema_name"."alias"
        }
}
"""


from typing import Dict, Tuple, List


class SQLRewriter:
    def __init__(self, model_info_dict: Dict[str, Dict], destination_nodes: List[Tuple[str]]):
        self.alias_counter = 0
        self.updated_dict = model_info_dict
        self.destination_nodes = destination_nodes

    def _replace_ref_with_sql(self, model_whose_code_to_update: str, model_whose_code_to_insert: str):
        """
        Say the code of `model_whose_code_to_update` looks like this:

            ... FROM db_name.schema.model_whose_code_to_insert ...

        Update to:

            ... FROM ( SQL Code from `model_whose_code_to_insert` ) AS alias{alias_counter}...
        """
        current_code = self.updated_dict[model_whose_code_to_update]['code']

        in_code_ref = self.updated_dict[model_whose_code_to_insert]['compiled_code_reference']
        sql_model_whose_code_to_insert = self.updated_dict[model_whose_code_to_insert]['code']

        new_code = current_code.replace(
            in_code_ref, f"( {sql_model_whose_code_to_insert} ) AS alias{self.alias_counter} "
        )

        self.alias_counter += 1

        self.updated_dict[model_whose_code_to_update]['code'] = new_code

    def _check_if_code_should_update(self, model_id: str) -> bool:
        """
        Recursively update the dict by replacing a direct reference to an upstream model with the
        sql code of said upstream model using _replace_ref_with_sql().

        If we reach a source table, let the immediate downstream model know it that it does not have
        to update its code, as it is fine to directly reference a source table.

        :returns:
        If return False, we are a source table. The models immediately downstream of us do not need
        to update their code.

        If return True, we are a model, and the model immediately downstream of us should update
        its reference to us by replacing it with our entire SQL query.
        """
        current_node_is_a_model = model_id in self.updated_dict

        if current_node_is_a_model:
            while len(self.updated_dict[model_id]['depends_on']) > 0:

                # By popping the dependencies, we make sure that we won't traverse the same path
                # on the DAG twice if we'd arrive at a certain node from two different directions
                next_dependency = self.updated_dict[model_id]['depends_on'].pop()

                if self._check_if_code_should_update(next_dependency):

                    self._replace_ref_with_sql(
                        model_whose_code_to_update=model_id,
                        model_whose_code_to_insert=next_dependency
                    )

        return current_node_is_a_model

    def update_all_sql_code(self):
        """
        We call _check_if_code_should_update() for each destination node. This recursively
        updates the code for that destination node, and all its predecessors. See
        _check_if_code_should_update() for a more detailed explanation.

        By doing this for all destination nodes, we've ensured that the entire DAG gets updated.
        """
        for destination_node_id_tuple in self.destination_nodes:
            _ = self._check_if_code_should_update(destination_node_id_tuple[0])
