from CwdChecker import CwdChecker
from YamlScraper import YamlScraper
import os


if __name__ == "__main__":
    cwd_checker = CwdChecker()
    cwd_checker.do_all_checks()
    profiles_yml_path = cwd_checker.get_profiles_path()

    yml_scraper = YamlScraper(profiles_yml_path)

    print(yml_scraper.extract_db_creds())
