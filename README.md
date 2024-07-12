## ViewSelectionAdvisor
Welcome to `ViewSelectionAdvisor`, a tool designed to inform dbt users about the problem of
model materialization. This tool consists of two separate packages working together, each with their
own GitHub repository:
* [A dbt package](https://github.com/bramreinders97/view_selection_tool_dbt)
* [A python package](https://github.com/bramreinders97/view_selection_tool_python)


## Installation Instructions
We assume you have a working dbt project for which you want advice. If so, follow the following
steps:

1. In not done already, follow the installation and usage instruction of 
[the dbt part](https://github.com/bramreinders97/view_selection_tool_dbt) of 
`ViewSelectionAdvisor`. The dbt part has to be run **before** the python part.


2. In a location which is convenient for you, either clone this repo by calling
   ```git clone https://github.com/bramreinders97/view_selection_tool_python.git```,    
or download the `src` folder from this repository. Ensure you know the absolute filepath
of the chosen location, you'll need it at the first step of the usage instructions.  


3. Ensure the following packages are installed in the `venv` that is used:
   ```toml
   ruamel-yaml = "^0.18.6"
   psycopg2 = "^2.9.9"
   ```

## Usage Instructions

1. Obtain the advice on which models to materialize:
From inside the root directory of your dbt project (from the same location as where you would call
`dbt run`), call `main.py`:  
   ```python path/to/src/main.py```   