# google-bigquery-data-modeller
Model your data using BigQuery views and Jinja templates

## Installation and usage

1. Authenticate with Google Cloud from your command line: `gcloud init`
2. Deploy a view with: 

```
./compile.py -m select_101.sql.j2 -v -d <DATASET> -p <PROJECTID>
```

## Configuration

## Variables

Variables may be declared in the file `configuration.json`. To use a variable in a template simply enclose it in ```{{ curlyBrackets }}```

## Deployments

Using the `-all` flag, all the views listed in `deployment.json` will be deployed.
