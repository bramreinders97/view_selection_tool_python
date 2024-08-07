"""YamlScraper class."""

import ruamel.yaml
import re
import os
from ruamel.yaml.comments import CommentedMap, CommentedSeq


class YamlScraper:
    def __init__(self, filepath: str):
        """Initialize YamlScraper class, and read contents of file."""
        self.filepath = filepath
        self.contents = self._read_and_process_contents()

    def _read_and_process_contents(self) -> CommentedMap:
        """Read the contents of a YAML file and replace env vars."""
        yaml = ruamel.yaml.YAML()
        with open(self.filepath, "r") as f:
            data = yaml.load(f)
        return self._replace_env_vars(data)

    def _replace_env_vars(self, data):
        """Recursively replace env vars in the YAML content."""
        if isinstance(data, CommentedMap):
            for key, value in data.items():
                data[key] = self._replace_env_vars(value)
        elif isinstance(data, CommentedSeq):
            for index, item in enumerate(data):
                data[index] = self._replace_env_vars(item)
        elif isinstance(data, str):
            data = self._replace_env_var_placeholders(data)
        return data

    @staticmethod
    def _replace_env_var_placeholders(value: str) -> str:
        """Replace env_var placeholders in a string."""
        # Enhanced pattern to allow spaces
        pattern = re.compile(r"\{\{\s*env_var\(\s*'([^']+)'\s*(?:,\s*'([^']*)')?\s*\)\s*\}\}")

        def replacer(match):
            env_var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else None
            return os.getenv(env_var_name, default_value)

        return pattern.sub(replacer, value)
