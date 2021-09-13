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
import string


MAPPING = {
    "dataset name": "dataset_name",
    "public description": "dataset_description",
    "originating organisation for data store": "source"
}

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(os.path.dirname(CURRENT_DIRECTORY), "content")


def to_camel_case(field):
    to_remove = ["(", ")", "/", ",", "'", '"']
    for i in to_remove:
        field = field.replace(i, "")
    field = field.strip().lower()
    field = field.replace(" ", "_")
    return field


def write_to_file(*args, category, new_file_name, template_name, context):
    directory = os.path.join(OUTPUT_DIR, f"_{category}")
    if not os.path.exists(directory):
        print(f"Creating {directory}")
        os.mkdir(directory)
    parent_dir = os.path.dirname(CURRENT_DIRECTORY)
    output_file = os.path.join(
        parent_dir, "content", f"_{category}", f"{new_file_name}.md"
    )
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(CURRENT_DIRECTORY)
    )
    template = env.get_template(template_name)
    with open(output_file, "w") as f:
        print(f"writing {output_file}")
        f.write(template.render(**context))


@click.command()
@click.argument('file_name')
def generate_data_elements(file_name):
    print(f"Deleting {OUTPUT_DIR}")
    shutil.rmtree(OUTPUT_DIR)
    print(f"Creating {OUTPUT_DIR}")
    os.mkdir(OUTPUT_DIR)

    populated_first_letters = set()

    # Generates all the data set pages
    with open(file_name) as f:
        csv_reader = csv.DictReader(f)
        missing = set(MAPPING.keys()) - set(i.lower() for i in csv_reader.fieldnames)
        if missing:
            raise ValueError(f"Missing fields, {missing}")
        for row in csv_reader:
            context = {}
            for csv_field_name, value in row.items():
                mapping = MAPPING.get(csv_field_name.lower())
                if not mapping:
                    continue
                if mapping.lower() == "dataset_description":
                    context[mapping] = value.strip()
                else:
                    context[mapping] = json.dumps(value.strip())

                if mapping == "dataset_name":
                    first_letter = to_camel_case(value)[0]

                    if first_letter.isnumeric():
                        first_letter = "0-9"
                    context["first_letter"] = first_letter.upper()
                    populated_first_letters.add(first_letter)

            write_to_file(
                category="data_elements",
                new_file_name=to_camel_case(context["dataset_name"]),
                template_name='data_element.md.jinja',
                context=context
            )

    first_letters = ["0-9"] + [i for i in string.ascii_uppercase]

    for first_letter in first_letters:
        context = {
            "name": first_letter,
            "populated": first_letter.lower() in populated_first_letters
        }
        write_to_file(
            category="datasets",
            new_file_name=first_letter.lower(),
            template_name="first_letter.md.jinja",
            context=context
        )


if __name__ == '__main__':
    generate_data_elements()
