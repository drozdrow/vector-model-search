""" Tests for main.py """
import sys
import os
import sqlite3
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import create_connection, search_movies, load_initial_data, get_tfidf_vector, calculate_norm, calculate_similarities, get_movie_names, find_similar_movies

@pytest.fixture(name="db_connection")
def fixture_db_connection():
    """Fixture for creating a temporary SQLite database connection."""
    conn = sqlite3.connect(":memory:")  # Using an in-memory database for testing
    setup_test_database(conn)  # insert test data
    yield conn
    conn.close()

def setup_test_database(conn):
    """Set up a test database schema and insert test data."""
    cur = conn.cursor()
    cur.execute("CREATE TABLE movies (wikipedia_movie_id INTEGER, movie_name TEXT, movie_genres TEXT, movie_release_date TEXT)")
    cur.execute("CREATE TABLE plot_summaries (wikipedia_movie_id INTEGER, plot_summary TEXT)")
    cur.execute("CREATE TABLE sparse_tfidf (wikipedia_movie_id INTEGER, tfidf_index INTEGER, tfidf_value REAL)")

    # Insert test data
    cur.execute("INSERT INTO movies VALUES (1, 'Test Movie', 'Action', '2020')")
    cur.execute("INSERT INTO movies VALUES (2, 'Another Test Movie', 'Drama', '2021')")
    cur.execute("INSERT INTO plot_summaries VALUES (1, 'This is a test plot summary.')")
    cur.execute("INSERT INTO plot_summaries VALUES (2, 'This is another test plot summary.')")
    cur.execute("INSERT INTO sparse_tfidf VALUES (1, 0, 0.5)")
    cur.execute("INSERT INTO sparse_tfidf VALUES (2, 0, 0.7)")
    conn.commit()

def test_create_connection():
    """Test creating a connection to the SQLite database."""
    conn = create_connection(":memory:")
    assert conn is not None
    conn.close()

def test_search_movies(db_connection):
    """Test searching movies by title."""
    results = search_movies(db_connection, 'Test')
    assert len(results) == 2
    assert results[0][0] == 'Test Movie'
    assert results[1][0] == 'Another Test Movie'

    results = search_movies(db_connection, 'Another')
    assert len(results) == 1
    assert results[0][0] == 'Another Test Movie'

def test_load_initial_data(db_connection):
    """Test loading initial data."""
    results = load_initial_data(db_connection)
    assert len(results) == 2
    assert results[0][0] == 'Another Test Movie'
    assert results[1][0] == 'Test Movie'

def test_get_tfidf_vector(db_connection):
    """Test getting the TF-IDF vector for a specific movie."""
    cur = db_connection.cursor()
    tfidf_vector = get_tfidf_vector(cur, 1)
    assert len(tfidf_vector) == 1
    assert tfidf_vector[0] == (0, 0.5)

    tfidf_vector = get_tfidf_vector(cur, 2)
    assert len(tfidf_vector) == 1
    assert tfidf_vector[0] == (0, 0.7)

def test_calculate_norm():
    """Test calculating the norm of a TF-IDF vector."""
    vector = {0: 0.5, 1: 0.5}
    norm = calculate_norm(vector)
    assert norm == pytest.approx(0.7071, 0.0001)

    vector = {0: 0.7, 1: 0.7}
    norm = calculate_norm(vector)
    assert norm == pytest.approx(0.9899, 0.0001)

def test_calculate_similarities(db_connection):
    """Test calculating cosine similarities."""
    current_vector = {0: 0.5}
    norm_current = calculate_norm(current_vector)
    cur = db_connection.cursor()
    cur.execute("SELECT wikipedia_movie_id, tfidf_index, tfidf_value FROM sparse_tfidf")
    all_vectors = cur.fetchall()

    similarities = calculate_similarities(current_vector, norm_current, all_vectors, 1)
    assert len(similarities) == 1
    assert similarities[2] == pytest.approx(0.7 * 0.5 / (0.5 * 0.7), 0.0001)

def test_get_movie_names(db_connection):
    """Test getting movie names for the given movie IDs."""
    cur = db_connection.cursor()
    movie_ids = [1, 2]
    movie_names = get_movie_names(cur, movie_ids)
    assert movie_names[1] == 'Test Movie'
    assert movie_names[2] == 'Another Test Movie'

def test_find_similar_movies(db_connection):
    """Test finding similar movies based on TF-IDF."""
    similar_movies = find_similar_movies(db_connection, 1)
    assert len(similar_movies) == 1
    assert similar_movies[0][0] == 'Another Test Movie'
    assert similar_movies[0][1] == pytest.approx(1.0, 0.0001)  # identical vectors

def test_find_similar_movies_no_results(db_connection):
    """Test finding similar movies when there are no results."""
    cur = db_connection.cursor()
    cur.execute("DELETE FROM sparse_tfidf WHERE wikipedia_movie_id=2")
    db_connection.commit()

    similar_movies = find_similar_movies(db_connection, 1)
    assert len(similar_movies) == 0
