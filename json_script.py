"""
        Format JSON field to a human-readable string.
"""
import csv
import json

tsv_file_path = 'sources/movie_metadata.tsv'
csv_file_path = 'sources/movie_metadata.csv'


def format_json_field(field):
    """
        Format JSON field to a human-readable string.

        Parameters:
            field (str): JSON field to be formatted.

        Returns:
            str: Formatted string.
    """
    try:
        # Loading data in JSON format and converting it to a list
        json_data = json.loads(field.replace('""', '"'))
        # Return a string listing elements (genre names only)
        return ', '.join([value for key, value in json_data.items()])
    except json.JSONDecodeError:
        return None


# Opening the original TSV file and creating a new CSV file
with open(tsv_file_path, 'r', encoding='utf-8') as tsv_file, open(csv_file_path, 'w', newline='',
                                                                  encoding='utf-8') as csv_file:
    tsv_reader = csv.reader(tsv_file, delimiter='\t')
    csv_writer = csv.writer(csv_file)

    for row in tsv_reader:
        # Processing Each JSON Field
        languages = format_json_field(row[6])
        countries = format_json_field(row[7])
        genres = format_json_field(row[8])

        # Preparing a string for writing to CSV, replacing JSON with a human-readable string
        row_to_write = row[:6] + [languages, countries, genres]

        csv_writer.writerow(row_to_write)
