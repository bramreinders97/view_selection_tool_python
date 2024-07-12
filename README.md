Based on the query plan as provided by calling [EXPLAIN in postgres](https://www.postgresql.org/docs/current/sql-explain.html), estimate which configuration (= a selection of specific models in the DAG to be materialized) will result in the lowest cost. 

This is done by the Orchestrator class `ViewSelectionAdvisor` in a bunch of steps:

(following along with the logic inside `ViewSelectionAdvisor` will hopefully give a clear view of the workflow)

1. Do necessary checks to see if the environment the user is calling the tool from is as we expect, if we do find unexpected stuff, raise an error
2. Creating the necessary helper classes which are needed to calculate which configuration is best
3. in `advise()` :
    1. loop over the possible configurations, and for each configuration estimate the total cost
    2. keep track of the smallest cost observed, while checking of this solution will fit in the db
    3. return the configuration with the lowest cost associated to it



## New part for docs
Welcome to the draft page of the repository of `ViewSelectionAdvisor`. If you've gotten this far, 
