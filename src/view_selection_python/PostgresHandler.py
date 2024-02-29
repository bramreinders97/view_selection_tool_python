import psycopg2
from typing import Tuple, List, Dict
from ruamel.yaml.comments import CommentedMap
from Exceptions.errors import NOT_ALL_TABLES_IN_VST_SCHEMA_ERROR

REQUIRED_TABLES = [
    'fct_avg_maintenance_fractions',
    'fct_all_models_plus_code',
    'fct_destination_nodes',
    'fct_model_dependencies'
]


class PostgresHandler:
    def __init__(self, db_creds: CommentedMap):
        self.db_host = db_creds['host']
        self.db_port = db_creds['port']
        self.db_name = db_creds['dbname']
        self.db_user = db_creds['user']
        self.db_password = db_creds['password']
        self.db_schema = db_creds['schema']
        self.conn = None
        self.cursor = None

        self._check_if_necessary_tables_present()

    def _open_connection(self):
        self.conn = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password
        )

        self.cursor = self.conn.cursor()

    def _close_connection(self):
        self.cursor.close()
        self.conn.close()

    def _get_tables_present_vst_schema(self) -> List[str]:
        """Retrieve a list of all tables in the view_selection_tool schema."""
        self._open_connection()

        query = "SELECT table_name " + \
                "FROM information_schema.tables " + \
                f"WHERE table_schema = '{self.db_schema}' " + \
                "AND table_type = 'BASE TABLE';"

        self.cursor.execute(query)
        present_tables = [row[0] for row in self.cursor.fetchall()]

        self._close_connection()

        return present_tables

    def _check_if_necessary_tables_present(self):
        """Check if the tables required for the tool to work are present in the DB"""
        present_tables = self._get_tables_present_vst_schema()

        missing_tables = [required_table for required_table in REQUIRED_TABLES if required_table not in present_tables]

        if len(missing_tables) > 0:
            raise RuntimeError(
                NOT_ALL_TABLES_IN_VST_SCHEMA_ERROR.format(
                    dbname=self.db_name,
                    schema=self.db_schema,
                    missing_tables="\n - ".join(missing_tables)
                )
            )

    def _execute_query(self, query) -> List[Tuple]:
        """Return all tuples from the provided query"""
        self._open_connection()

        self.cursor.execute(query)
        all_rows = self.cursor.fetchall()

        self._close_connection()
        return all_rows

    def _get_table_content(self, table_name: str, cols: str = '*') -> List[Tuple]:
        """Return all tuples from the table `table_name`"""
        query = f"SELECT {cols} " + \
                f"FROM {self.db_schema}.{table_name};"
        result = self._execute_query(query)
        return result

    def get_all_models_and_code(self) -> List[Tuple[str]]:
        return self._get_table_content('fct_all_models_plus_code')

    def get_destination_nodes(self) -> List[Tuple[str]]:
        return self._get_table_content('fct_destination_nodes')

    def get_model_dependencies(self) -> List[Tuple[str]]:
        return self._get_table_content('fct_model_dependencies')

    def get_maintenance_fractions(self) -> List[Tuple[str]]:
        return self._get_table_content('fct_avg_maintenance_fractions', cols='model_id, avg_maintenance_fraction')

    def get_storage_space_left(self) -> int:
        """Return the #bytes left in the DB at this moment in time"""
        query = f"SELECT pg_database_size('{self.db_name}');"
        bytes_left = self._execute_query(query)[0][0]
        return bytes_left

    def get_output_explain(self, query_to_explain: str) -> List[Dict]:
        """Execute the EXPLAIN statement on `query_to_explain` and return the query plan in JSON format"""
        explain_query = f"EXPLAIN (FORMAT JSON) {query_to_explain}"
        query_plan = self._execute_query(explain_query)[0][0]
        return query_plan
