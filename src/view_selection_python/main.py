from CwdChecker import CwdChecker
from YamlScraper import YamlScraper
from PostgresHandler import PostgresHandler


if __name__ == "__main__":
    cwd_checker = CwdChecker()
    cwd_checker.do_all_checks()
    profiles_yml_path = cwd_checker.get_profiles_path()

    yml_scraper = YamlScraper(profiles_yml_path)

    db_creds = yml_scraper.extract_db_creds()

    postgres = PostgresHandler(db_creds)

    all_models_and_code = postgres.get_models_and_code()

    for model, code in all_models_and_code:
        print(model)
        print(postgres.get_output_explain(code))
        print()

