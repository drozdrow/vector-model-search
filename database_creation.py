"""
    Creates a SQLite database and loads data from CSV and TXT files.
"""
import sqlite3
import pandas as pd

def create_database(metadata_csv_path, plot_summaries_txt_path, db_path):
    """
        Parameters:
            metadata_csv_path (str): Path to the CSV file containing movie metadata.
            plot_summaries_txt_path (str): Path to the TXT file containing plot summaries of movies.
            db_path (str): Path to save the SQLite database.

        Returns:
            str: Path to the created SQLite database.
    """
    metadata_df = pd.read_csv(metadata_csv_path, header=None, names=[
        "wikipedia_movie_id", "freebase_movie_id", "movie_name",
        "movie_release_date", "movie_box_office_revenue", "movie_runtime",
        "movie_languages", "movie_countries", "movie_genres"
    ])

    summaries_df = pd.read_csv(
        plot_summaries_txt_path,
        header=None,
        names=["wikipedia_movie_id", "plot_summary"],
        sep='\t'
    )

    conn = sqlite3.connect(db_path)

    metadata_df.to_sql('movies', conn, if_exists='replace', index=False)
    summaries_df.to_sql('plot_summaries', conn, if_exists='replace', index=False)

    conn.close()

    return db_path
