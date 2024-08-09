# ViewSelectionAdvisor

Welcome to `ViewSelectionAdvisor`, a tool designed to help dbt users address the problem of model materialization. 
This tool consists of two separate packages, each hosted in its own GitHub repository:
* [A dbt package](https://github.com/bramreinders97/view_selection_tool_dbt). 
This package is dependent on another dbt package: [Elementary](https://docs.elementary-data.com/guides/modules-overview/dbt-package)
* [A python package](https://github.com/bramreinders97/view_selection_tool_python)

### What does it do?
Most dbt projects are structured with a DAG that includes staging, intermediate, and marts models. Typically, staging and intermediate models are stored as views, while marts models are stored as tables. However, this default configuration may not always be the most efficient from a performance perspective. Determining which models should be materialized and which should not can be challenging.
This is where `ViewSelectionAdvisor` comes in to help. By using this tool, you are advised on the best 
materialization strategy for you models in dbt. 


### How does it work?
`ViewSelectionAdvisor` determines the optimal configuration of materialized models by evaluating all possible configurations. For each configuration, it estimates the total cost of building your entire DAG using PostgreSQL's `EXPLAIN` command.

Note: `ViewSelectionAdvisor` assumes that all [destination nodes](## "Destination nodes are nodes in your DAG without an outgoing edge. In most cases, these nodes correspond to mart tables.") are already materialized as tables. Consequently, these nodes will not appear in the provided advice.

Note 2: By default, `ViewSelectionAdvisor` only looks at materialization configurations of at most 2 models. 
This can be changed using the `max_materializations` variable (see [overview of variables](#possible-variables-for-vst-advise)).


### A note on Elementary's defaults materializations warning
Please note that when running any of the `dbt run` commands in the coming steps, it is possible that you observe
a warning from dbt on elementary trying to override default materializations. 
This is not a problem, as [the developers of Elementary are aware of this and working on a solution](https://docs.elementary-data.com/oss/quickstart/quickstart-cli-package#important-allowing-elementary-to-override-dbts-default-materializations-relevant-from-dbt-1-8).
Furthermore, the parts of the elementary package that are affected by this are not relevant for `ViewSelectionAdvisor`.

## Installation Instructions

### dbt part
1. Include `ViewSelectionAdvisor` in your `packages.yml` file:
    ```yaml
      - git: "https://github.com/bramreinders97/view_selection_tool_dbt.git"
        revision: 7a6d08f923c50d8930fcbdc0dca1ab23bc934520
    ``` 
 
2. Update your `dbt_project.yml` file:

    - **Schema Configuration**:
      Specify the schema appendix where dbt should store the relevant tables:
      ```yaml
        models:
          elementary:
            +schema: elementary
          view_selection_tool:
            +schema: view_selection_tool
      ```
      These settings ensure that if your project's tables are stored in schema `x`, then the tables from `elementary` will be stored in `x_elementary`, and those from `ViewSelectionAdvisor` will be stored in `x_view_selection_tool`.

    - **Variable Configuration**:
      Set the following variables:
      ```yaml
        vars:
          view_selection_tool:
            # Database where the elementary tables are located
            # (same as in your target profile from profiles.yml)
            elementary_src_db:  

            # Schema where the elementary tables are stored (e.g., `x_elementary`)
            src_schema:  

            # Name of your project as specified in this dbt_project.yml
            relevant_package:  
      ```
      This information allows `ViewSelectionAdvisor` to identify the data sources (`elementary_src_db` and `src_schema`) and the models to focus on (`relevant_package`).


3. Import the packages and build Elementary models
   ```shell
   dbt deps
   dbt run --select elementary
   ```
   This will install both the `view_selection_tool` and `elementary` packages, and create empty tables for Elementary to fill (at schema `x_elementary`).



### Python part

4. Install the package using your preferred method:
   ```shell
   pip install view-selection-python
   ```
   or
   ```shell
   poetry add view-selection-python
   ```


## Usage Instructions
Because `ViewSelectionAdvisor` relies entirely on the tables created by Elementary, it is crucial to ensure these tables are populated with the necessary information before running `ViewSelectionAdvisor`. Whenever you want to receive advice on the materialization of a DAG in dbt, follow these steps:

1. Populate Elementary tables with the latest information:
   ```shell
   dbt run --select <your_project_name>
   ```
   Running your project populates the Elementary tables with the data required by ViewSelectionAdvisor.

   _Note: This command only runs the models in your project, not the individual models from Elementary. However, the on-run-end hook of Elementary will execute automatically and provide all the necessary data._


2. Run `ViewSelectionAdvisor`:
   
   - **Transform Info From Elementary**:
   ```shell
   dbt run --select view_selection_tool
   ```
   This transforms the information provided in the Elementary tables and
   fills the database schema `x_view_selection_tool` with all information the
   python part of the `ViewSelectionAdvisor` requires in order to give a proper advice.

   - **Transform Info From Elementary**:
   ```shell
   vst-advise
   ```
   This command compares all possible materialization configurations, and advises on the configuration with 
   the lowest estimated cost. 

### Output Explanation
`ViewSelectionAdvisor` bases its suggestions on an estimate of the number of bytes processed when running your entire DAG. 
The displayed percentages correspond to the expected **difference in bytes processed compared to the default materialization setting**, which only materializes the [destination nodes](## "Destination nodes are nodes in your DAG without an outgoing edge. In most cases, these nodes correspond to mart tables.").

#### Example Output:

Below is an example output from the `ViewSelectionAdvisor`. Each row represents a specific configuration of models considered for materialization, along with the corresponding percentage difference in bytes processed compared to the default setting.

```shell
+----------------------------------------------------------------------------------------------------------------+---------------------------+
|                                                     Config                                                     | % Difference with default |
+----------------------------------------------------------------------------------------------------------------+---------------------------+
|          ('model.dbt_glue_proj.stg_imdb__name_basics', 'model.dbt_glue_proj.stg_imdb__title_basics')           |         -91.055%          |
|          ('model.dbt_glue_proj.stg_imdb__title_basics', 'model.dbt_glue_proj.stg_imdb__title_crews')           |         -85.157%          |
| ('model.dbt_glue_proj.stg_imdb__title_basics', 'model.dbt_glue_proj.int_directors_flattened_from_title_crews') |         -84.762%          |
+----------------------------------------------------------------------------------------------------------------+---------------------------+
```

#### Columns Explained:

- **Config**: This column lists the selected models within the DAG that are considered for materialization in the given configuration.

- **% Difference with default**: This column shows the percentage difference in the number of bytes processed when using the given configuration compared to the default materialization setting. A negative percentage indicates a reduction in bytes processed, a positive percentage an increase. 



### Possible Variables for `vst-advise`
The following variables can be used to change the behavior of `vst-advise`: 

| Option                                                                        | Description                                                                                                                                  |
|-------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `-h`, `--help`                                                                | Show this help message and exit                                                                                                              |
| `-mm <MAX_MATERIALIZATIONS>`, `--max_materializations <MAX_MATERIALIZATIONS>` | Set the maximum number of models to consider for materialization. Higher values provide more options but may increase runtime. Default is 2. |
| `-p <PROFILE>`, `--profile <PROFILE>`                                         | Select the profile to use                                                                                                                    |
| `-t <TARGET>`, `--target <TARGET>`                                            | Select the target profile to use                                                                                                             |
| `-x <TOP_X>`, `--top_x <TOP_X>`                                               | Select the top x configurations to print in the terminal. Default is 10.                                                                     |

