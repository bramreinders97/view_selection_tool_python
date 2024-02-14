import ruamel.yaml
from ruamel.yaml.comments import CommentedMap
from Exceptions.errors import (NO_VST_PROFILE_ERROR, NOT_POSTGRES_ERROR, NO_OUTPUTS_ERROR,
                               NO_DEFAULT_ERROR, MISSING_CRED_ERROR)


def _check_content(required_key: str, content_to_check: CommentedMap, error_msg: str):
    """
    Check if a specified key is in the CommentedMap, raise error if not
    """
    if required_key not in content_to_check:
        raise RuntimeError(
            error_msg
        )


class YamlScraper:
    def __init__(self, filepath: str, profile_name_key: str = 'view_selection_tool',
                 outputs_key: str = 'outputs', target_name_key: str = 'default'):

        self.filepath = filepath
        self.profile_key = profile_name_key
        self.outputs_key = outputs_key
        self.target_key = target_name_key
        self.contents = self._read_contents()
        self._do_checks()

    def _read_contents(self) -> CommentedMap:
        """Read the contents of a yaml file"""
        yaml = ruamel.yaml.YAML()
        with open(self.filepath, 'r') as f:
            data = yaml.load(f)
        return data

    def _has_vst_profile(self):
        """
        Check if there is a profile called `view_selection_tool`.
        Raise error if not.
        """
        _check_content(self.profile_key, self.contents, NO_VST_PROFILE_ERROR)

    def _has_outputs(self):
        """
        Verify that `outputs` is mentioned in the profiles.yml is like this:
        view_selection_tool -> outputs
        """
        _check_content(self.outputs_key, self.contents[self.profile_key], NO_OUTPUTS_ERROR)

    def _has_default(self):
        """
        Verify that `default` is mentioned in the profiles.yml is like this:
        view_selection_tool -> outputs -> default
        """
        _check_content(self.target_key, self.contents[self.profile_key][self.outputs_key], NO_DEFAULT_ERROR)

    def _check_if_all_db_creds_present(self):
        """Check if all necessary creds are present. Raise error if not"""
        needed_creds = ['host', 'port', 'user', 'password', 'dbname', 'schema']
        db_creds = self.contents[self.profile_key][self.outputs_key][self.target_key]

        for needed_cred in needed_creds:
            _check_content(
                required_key=needed_cred,
                content_to_check=db_creds,
                error_msg=MISSING_CRED_ERROR.format(credential=needed_cred)
            )

    def _check_if_postgres(self):
        """Check if the specified type is `postgres`, if not raise an error"""
        if self.contents[self.profile_key][self.outputs_key][self.target_key]['type'] != 'postgres':
            raise ValueError(
                NOT_POSTGRES_ERROR
            )

    def _do_checks(self):
        """
        Check the structure of the provided YAML file step by step to ensure that it is as expected
        """
        self._has_vst_profile()
        self._has_outputs()
        self._has_default()
        self._check_if_all_db_creds_present()
        self._check_if_postgres()

    def extract_db_creds(self) -> CommentedMap:
        """Return the credentials of the db"""
        return self.contents[self.profile_key][self.outputs_key][self.target_key]
