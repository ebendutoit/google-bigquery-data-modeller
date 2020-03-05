# google-bigquery-data-modeller
Model your data using BigQuery views and Jinja templates

## Installation and usage

1. Authenticate with Google Cloud from your command line: `gcloud init`
2. Deploy a view with: 

```

./compile.py -m select_101.sql.j2 -v -d <DATASET> -p <PROJECTID>
```
