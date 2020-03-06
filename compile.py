#!/usr/bin/env python3

import argparse
import json
import os
import sys
from clint.textui import puts, colored, indent
from google.cloud import bigquery
from jinja2 import Template, FileSystemLoader, Environment
from os import path
from pygments import highlight
from pygments.lexers.sql import SqlLexer
from pygments.formatters import TerminalFormatter
from pyfiglet import Figlet

# Configuration load
with open(path.join(".", "configuration", "configuration.json")) as json_config:
    config_dict = json.load(json_config)

def create_view(dataset_name, view_name, project, viewSQL):

    f = Figlet(font='slant')
    print (f.renderText(view_name.replace("_", " ")))

    view_description = get_view_description(view_name)

    bigquery_client = bigquery.Client(project=project)

    job_config = bigquery.CopyJobConfig()
    job_config.write_disposition = "WRITE_TRUNCATE"

    dataset = bigquery_client.dataset(dataset_name)
    table_ref = dataset.table(view_name)
    table = bigquery.Table(table_ref)
    table.view_query = viewSQL
    table.view_use_legacy_sql = False
    table.description = view_description['metric_description']

    try:
        # Delete the view if it exists
        bigquery_client.delete_table(table)
        with indent(4, quote='* '):
            puts(colored.blue('Existing view deleted'))
    except Exception as err:
        with indent(4, quote='* '):
            puts(colored.red("View doesn't exist"))

    try:
        # Create the new view
        bigquery_client.create_table(table)
        with indent(4, quote='* '):
            puts(colored.blue("View created : {}".format(".".join([project, dataset_name, view_name]))))
    except Exception as err:
        print(err)
        with indent(4, quote='* '):
            puts(colored.red("Error: Couldn't create view"))
        return False

    view_update = bigquery.Table(table_ref,schema=get_schema_from_description(view_description))
    view_update = bigquery_client.update_table(view_update,['schema'])
    with indent(4, quote='* '):
        puts(colored.blue("Updated the view schema descriptions"))

    return True

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def get_schema_from_description(view_description):
    with indent(4, quote='* '):
        puts(colored.blue("Getting the view schema from the description json file"))

    view_schema = []
    for item in view_description['fields']:
        mode = "NULLABLE"
        if "mode" in item:
            mode = item["mode"]
        view_schema.append(bigquery.SchemaField(item['field'], item['type'], mode=mode, description=item['description']))
    return view_schema

def get_view_description(view_name):

    json_file = find(view_name+".json", "./")
    with indent(4, quote='* '):
        puts(colored.green("Found the description file at --> " + json_file))

    with open(json_file) as json_file:  
        view_description = json.load(json_file)
    return view_description

def render_template(template_file, output_file):
    location = find(template_file, "metrics/").replace("metrics", "")
    template_file = path.join(template_file.split(".")[0], template_file)
    # Template render
    template_loader = FileSystemLoader(searchpath="metrics/")
    template_env = Environment(loader=template_loader)
    TEMPLATE_FILE = location
    with indent(4, quote='* '):
        puts(colored.green("Going to render template file at --> " + location))
    with indent(4, quote='* '):
        puts(colored.green("Rendered SQL --> "))

    template = template_env.get_template(TEMPLATE_FILE)
    output_text = template.render(config_dict)

    if (output_file):
        filename = path.join(".", "build", output_file)
        os.makedirs(path.dirname(filename), exist_ok=True)
        with open(filename, "w+") as text_file:
            print(output_text, file=text_file)
            return output_text
    else:
        print(highlight(output_text, SqlLexer(), TerminalFormatter(style='monokai')))
        return output_text
     
def deploy_all(dataset_name):
    json_file = find("deployment.json", "./")
    with open(json_file) as json_file:  
        all_views = json.load(json_file)

    for basename, viewname in all_views.items():
        final_sql = render_template(f"{basename}.sql.j2", f"{basename}.sql")
        create_view(dataset_name, viewname, "mydata-1470162410749", final_sql)



def main():
    
    DATASET = ""
    PROJECT = ""

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-m", "--metric_file", metavar="METRIC", action="store", help="the metric filename to process")
    parser.add_argument("-o", "--output_file", metavar="OUTPUTFILE", action="store")
    parser.add_argument("-v", "--create_view", action="store_true", help="create a view from the metric")
    parser.add_argument("-a", "--all_metrics", action="store_true", help="deploy all views")
    parser.add_argument("-d", "--dataset", metavar="DATASET", action="store", help="deploy views to this dataset")
    parser.add_argument("-p", "--project", metavar="PROJECT", action="store", help="deploy views to a dataset in this project")

    args = parser.parse_args()  

    if not (args.all_metrics or args.metric_file):
        parser.print_usage()
        sys.exit(1)
        
    if (not args.all_metrics):
        with indent(4, quote="* "):
            puts(colored.green("Metric file is ['{}']".format(args.metric_file)))
            if (args.output_file):
                puts(colored.green("Output file is ['{}']".format(args.output_file)))
            puts(colored.blue("Rendering ['{}']".format(args.metric_file.replace(".j2", ""))))

        finalSQL = render_template(args.metric_file, args.output_file)

        if (args.create_view):
            view_sql = finalSQL
            view_name = args.metric_file.split(".")[0]
            create_view(args.dataset, view_name, args.project, view_sql)

        if (args.output_file):
            print("...SQL File built at ./build/{}".format(args.output_file))
    else:
        deploy_all(args.dataset)

    with indent(4, quote="* "):
        puts(colored.yellow("Finished!"))
      
if __name__ == "__main__":
   main()
