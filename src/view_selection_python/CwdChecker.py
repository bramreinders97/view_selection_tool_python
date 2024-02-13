import os
from CLI import get_wd
from typing import List

# Define error messages
ERROR_DBT_PROJECT_NOT_FOUND = "This command must be called from inside a dbt project. " \
                              "However, a `dbt_project.yml` or `dbt_project.yaml` file was not found " \
                              "in the current working directory."
ERROR_VST_NOT_INSTALLED = "It seems like the dbt package `view_selection_tool` is not installed " \
                          "in your dbt project. Please make sure it is installed.\n" \
                          "Note that this command should be run from the root folder of your dbt project. " \
                          "If the package is installed correctly, the following path should be present: " \
                          "`dbt_packages/view_selection_tool`."
ERROR_PROFILES_NOT_FOUND = "The current working directory should contain a file called `profiles.yml` " \
                           "or `profiles.yaml`. However, no such file was found in the working directory."
PROFILE_PATH_NOT_SET_WARNING = "The profile path has not been recognized correctly. This is either due to " \
                            "necessary checks on the environment failing, or not being performed.\n" \
                            "Make sure that the do_all_checks() function runs without raising any errors, " \
                            "this will ensure that we obtain the correct file path."


class CwdChecker:
    def __init__(self):
        """If we're done with developing and ready to deploy as PyPi package,
        the working dir can probably be obtained using os.getcwd()"""
        self.cwd = get_wd()
        self.profile_path = None

    def _check_exists_and_return_path(self, file_names: List[str], error_message: str) -> str:
        """
        Check if any of the provided file names exist in the current working directory.
        If not, raise a RuntimeError with the provided error message.
        If found, return the path of the first existing file.
        """
        for file_name in file_names:
            file_path = os.path.join(self.cwd, file_name)
            if os.path.exists(file_path):
                return file_path

        # Not completely sure if this is the right type of Error to
        # raise, I asked chatGPT, and he came with RuntimeError(), but
        # should maybe double-check that
        raise RuntimeError(error_message)

    def _is_dbt_project(self):
        """
        -> dbt_project.y(a)ml should be there
        """
        _ = self._check_exists_and_return_path(
            file_names=['dbt_project.yml', 'dbt_project.yaml'],
            error_message=ERROR_DBT_PROJECT_NOT_FOUND)

    def _is_vst_installed(self):
        """
        -> dbt_packages/view_selection_tool should be an existing sub-folder
        """
        _ = self._check_exists_and_return_path(
            file_names=[os.path.join('dbt_packages', 'view_selection_tool')],
            error_message=ERROR_VST_NOT_INSTALLED)

    def _has_profile_yml(self):
        """
        -> profiles.y(a)ml should be there. If found, return the exact file path
        """
        self.profile_path = self._check_exists_and_return_path(
            file_names=['profiles.yml', 'profiles.yaml'],
            error_message=ERROR_PROFILES_NOT_FOUND)

    def do_all_checks(self):
        """
        If we get to the end of this function, all checks have passed
        """
        self._is_dbt_project()
        self._is_vst_installed()
        self._has_profile_yml()

    def get_profiles_path(self) -> str:
        """
        Return the path where we can find profiles.y(a)ml
        """
        if self.profile_path:
            return self.profile_path
        else:
            raise Warning(
                PROFILE_PATH_NOT_SET_WARNING
            )
