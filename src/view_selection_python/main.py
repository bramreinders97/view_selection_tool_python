from CwdChecker import CwdChecker
from YamlScraper import YamlScraper
from PostgresHandler import PostgresHandler
from SQLRewriter import SQLRewriter


if __name__ == "__main__":
    cwd_checker = CwdChecker()
    cwd_checker.do_all_checks()
    profiles_yml_path = cwd_checker.get_profiles_path()

    yml_scraper = YamlScraper(profiles_yml_path)

    db_creds = yml_scraper.extract_db_creds()

    # postgres = PostgresHandler(db_creds)

    # all_models_and_code = postgres.get_table_content('fct_all_models_plus_code')
    # destination_nodes = postgres.get_table_content('fct_destination_nodes')
    # model_dependencies = postgres.get_table_content('fct_model_dependencies')

    # TEST
    all_models_and_code = [
        ('B', 'z.s.A X'),
        ('C', 'z.s.B Y'),
        ('D', 'z.s.C Z')
    ]

    destination_nodes = [('D',)]

    model_dependencies = [
        ('B', "['A']", 'z.s.B'),
        ('C', "['B']", 'z.s.C'),
        ('D', "['C']", 'z.s.D')
    ]

    print(all_models_and_code[0])
    print(destination_nodes[0])
    print(model_dependencies[0])

    sql_rewrite = SQLRewriter(all_models_and_code, destination_nodes, model_dependencies)

    print(sql_rewrite.get_updated_code_per_model())
