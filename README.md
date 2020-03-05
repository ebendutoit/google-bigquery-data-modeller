# google-bigquery-data-modeller
Model your data using BigQuery views and Jinja templates

## Installation and usage

1. Authenticate with Google Cloud from your command line: `gcloud init`
   
2. Deploy a view with: 

```
./compile.py -m select_101.sql.j2 -v -d <DATASET> -p <PROJECTID>
```

3. Reference SQL templates from other templates:

```
SELECT *
FROM (
    {% include 'select_101/select_101.sql.j2' %}
)
```

4. Define the schema of views in a `json` file. One file per metric.

## Configuration

## Variables

Variables may be declared in the file `configuration.json`. To use a variable in a template simply enclose it in curly brackets like so:
```{{ variable_name }}```

## Deployments

Using the `-all` flag, all the views listed in `deployment.json` will be deployed.
