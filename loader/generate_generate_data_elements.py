#
# Accepts a csv. Expects the fields the fields below (case insensitive)
# outputs a data element for jekyll in the correct place
#

import click
import csv
import jinja2
import os
import shutil
import json

EXPECTED_FIELDS = [
    "dataset name",
    "Dataset description",
    "source",
    "granularity",
    "purpose of the data",
    "data controller",
    "dpia inclusion",
    "data processor organisations",
    "collecting and sharing governance"
]

OUTPUT_DIR = "content/_data_elements/"
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def to_camel_case(field):
    to_remove = ["(", ")", "/", ",", "-", "'", '"']
    for i in to_remove:
        field = field.replace(i, "")
    field = field.strip().lower()
    field = field.replace(" ", "_")
    return field


@click.command()
@click.argument('file_name')
def generate_generate_data_elements(file_name):
    parent_dir = os.path.dirname(CURRENT_DIRECTORY)
    output_dir = os.path.join(parent_dir, OUTPUT_DIR)
    print(f"Deleting {output_dir}")
    shutil.rmtree(output_dir)
    print(f"Creating {output_dir}")
    os.mkdir(output_dir)
    expected_fields = [
        to_camel_case(i) for i in EXPECTED_FIELDS
    ]

    with open(file_name) as f:
        csv_reader = csv.DictReader(f)
        found = sorted([to_camel_case(i) for i in csv_reader.fieldnames])
        expected = sorted([to_camel_case(i) for i in EXPECTED_FIELDS])
        if not set(found) == set(expected_fields):
            raise ValueError(f"Expected fields, {expected}, found {found}")
        for row in csv_reader:
            context = {}
            for k, v in row.items():
                if k == "Dataset description":
                    context[to_camel_case(k)] = v.strip()
                else:
                    context[to_camel_case(k)] = json.dumps(v.strip())
            file_name = "{}.md".format(to_camel_case(context["dataset_name"]))
            abs_file_name = os.path.join(output_dir, file_name)
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(CURRENT_DIRECTORY)
            )
            template = env.get_template('data_element.md.jinja')
            with open(abs_file_name, "w") as f:
                print(f"writing {file_name}")
                f.write(template.render(**context))


if __name__ == '__main__':
    generate_generate_data_elements()
