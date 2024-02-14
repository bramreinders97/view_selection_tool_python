"""YamlScraper"""

NO_VST_PROFILE_ERROR = "There is no profile called `view_selection_tool` mentioned in profiles.yml. " \
                       "Make sure to include this profile as mentioned in the documentation at LINK TO RIGHT DOCS"

NOT_POSTGRES_ERROR = "The `type` as mentioned in profiles.yml is expected to be `postgres`. At this moment " \
                     "in time, the ViewSelectionTool only works with Postgres DB."

NO_OUTPUTS_ERROR = "'outputs' not specified in profile 'view_selection_tool', please refer to the documentation " \
                   "to see how profiles.yml should be constructed. LINK TO DOCS"

NO_DEFAULT_ERROR = "Target named 'default' is not mentioned in the outputs of profile 'view_selection_tool', " \
                   "please refer to the documentation to see how profiles.yml should be constructed. LINK TO DOCS"

MISSING_CRED_ERROR = "'{credential}' is not specified in the default target in profiles.yml, please make sure it is " \
                     "specified as shown in the documentation, see LINK TO DOCS."

"""CwdChecker"""

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

"""PostgresHandler"""

NOT_ALL_TABLES_IN_VST_SCHEMA_ERROR = (
    "For the view selection tool to work correctly, the following tables should be "
    "present inside {dbname}.{schema}, but are not found:\n"
    " - {missing_tables}\n"
    "Please make sure the dbt code of the view_selection_tool is run correctly."
)
