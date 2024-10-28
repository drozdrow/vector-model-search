"""
   Delete movies from the database that do not have summaries.
"""
import sqlite3

def create_connection(db_file):
    """
    Create a connection to the SQLite database.

    Parameters:
        db_file (str): The path to the SQLite database file.

    Returns:
        Connection: A connection object to the SQLite database.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def delete_movies_without_summaries(db_conn):
    """
    Delete movies from the database that do not have summaries.

    Parameters:
        db_conn (Connection): A connection object to the SQLite database.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT m.wikipedia_movie_id FROM movies m
        LEFT JOIN plot_summaries ps ON m.wikipedia_movie_id = ps.wikipedia_movie_id
        WHERE ps.plot_summary IS NULL
    """)
    movies_to_delete = cur.fetchall()
    print("Movies to be deleted:", movies_to_delete)

    cur.execute("""
        DELETE FROM movies WHERE wikipedia_movie_id IN (
            SELECT m.wikipedia_movie_id FROM movies m
            LEFT JOIN plot_summaries ps ON m.wikipedia_movie_id = ps.wikipedia_movie_id
            WHERE ps.plot_summary IS NULL
        )
    """)
    db_conn.commit()

    print("Deleted movies without summaries.")

if __name__ == "__main__":
    connection = create_connection('movies.db')
    delete_movies_without_summaries(connection)
    connection.close()
