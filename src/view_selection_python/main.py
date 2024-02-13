from CwdChecker import CwdChecker
import os


if __name__ == "__main__":
    cwd_checker = CwdChecker()
    cwd_checker.do_all_checks()
    profiles_yml_path = cwd_checker.get_profiles_path()
    print(profiles_yml_path)