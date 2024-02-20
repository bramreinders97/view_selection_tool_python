from CwdChecker import CwdChecker
from YamlScraper import YamlScraper
from PostgresHandler import PostgresHandler
from SQLRewriter import SQLRewriter
from CostEstimator import CostEstimator


if __name__ == "__main__":
    cwd_checker = CwdChecker()
    cwd_checker.do_all_checks()
    profiles_yml_path = cwd_checker.get_profiles_path()

    yml_scraper = YamlScraper(profiles_yml_path)

    db_creds = yml_scraper.extract_db_creds()

    postgres = PostgresHandler(db_creds)

    all_models_and_code = postgres.get_table_content('fct_all_models_plus_code')
    destination_nodes = postgres.get_table_content('fct_destination_nodes')
    model_dependencies = postgres.get_table_content('fct_model_dependencies')

    sql_rewrite = SQLRewriter(all_models_and_code, destination_nodes, model_dependencies)

    # get postgres output with updated code
    new_code = sql_rewrite.get_updated_code_per_model()['model.dbt_chatGPT_suggestion.grouped_transactions_unioned_with_original']['code']
    # new_code =sql_rewrite.get_updated_code_per_model()['model.dbt_chatGPT_suggestion.stg_accounts']['code']
    explain_output = postgres.get_output_explain(new_code)

    cost_estimator = CostEstimator()
    cost_estimator.estimate_cost(explain_output)

    print(cost_estimator.get_storage_cost())
    print(cost_estimator.get_execution_cost())


    # get postgres output as before
    # for model, code in all_models_and_code:
    #     # if model == 'model.dbt_chatGPT_suggestion.int_accounts_and_groups_joined':
    #     #     explain_output = postgres.get_output_explain(code)
    #     #     break
    #     print(model)

    # print(code)
    #