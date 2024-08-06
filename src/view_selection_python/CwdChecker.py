"""CwdChecker class."""

import os
from typing import List

from .CLI import get_wd
from .Exceptions.errors import (
    ERROR_DBT_PROJECT_NOT_FOUND,
    ERROR_PROFILES_NOT_FOUND,
    ERROR_VST_NOT_INSTALLED,
)
from .Exceptions.warnings import PROFILE_PATH_NOT_SET_WARNING


class CwdChecker:
    """CwdChecker class.

    This class checks if the user calls the tool from a correct working directory.
    These checks are necessary to ensure that the rest of the tool functions properly.
    """

    def __init__(self):
        """Initialize class.

        If we're done with developing and ready to deploy as PyPi package,
        the working dir can probably be obtained using os.getcwd()
        """
        self.cwd = get_wd()
        self.profile_path = None

    def _check_exists_and_return_path(
        self, file_names: List[str], error_message: str
    ) -> str:
        """Return the exact path of file if it exists.

        Check if any of the provided file names exist in the current working directory.
        If not, raise a RuntimeError with the provided error message.
        If found, return the path of the correct path.
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
        """dbt_project.y(a)ml should be there."""
        _ = self._check_exists_and_return_path(
            file_names=["dbt_project.yml", "dbt_project.yaml"],
            error_message=ERROR_DBT_PROJECT_NOT_FOUND,
        )

    def _is_vst_installed(self):
        """dbt_packages/view_selection_tool should be an existing sub-folder."""
        _ = self._check_exists_and_return_path(
            file_names=[os.path.join("dbt_packages", "view_selection_tool")],
            error_message=ERROR_VST_NOT_INSTALLED,
        )

    def _has_profile_yml(self):
        """profiles.y(a)ml should be there. If found, return the exact file path."""
        self.profile_path = self._check_exists_and_return_path(
            file_names=["profiles.yml", "profiles.yaml"],
            error_message=ERROR_PROFILES_NOT_FOUND,
        )

    def do_all_checks(self):
        """If we get to the end of this function, all checks have passed."""
        self._is_dbt_project()
        self._is_vst_installed()
        self._has_profile_yml()

    def get_profiles_path(self) -> str:
        """Return the path where we can find profiles.y(a)ml."""
        if self.profile_path:
            return self.profile_path
        else:
            raise Warning(PROFILE_PATH_NOT_SET_WARNING)
