""" Tests for vector_model.py """
import sys
import os
import sqlite3
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vector_model import create_connection, setup_database, preprocess_text, save_tfidf_values, process_and_save_documents

nltk.download('punkt')
nltk.download('stopwords')
@pytest.fixture(name="db_connection")
def fixture_db_connection():
    """Fixture for creating a temporary SQLite database connection."""
    conn = sqlite3.connect(":memory:")  # Using an in-memory database for testing
    setup_database(conn)
    yield conn
    conn.close()

def test_create_connection():
    """Test creating a connection to the SQLite database."""
    conn = create_connection(":memory:")
    assert conn is not None
    conn.close()

def test_setup_database(db_connection):
    """Test setting up the database."""
    cur = db_connection.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sparse_tfidf';")
    table = cur.fetchone()
    assert table is not None

def test_preprocess_text():
    """Test preprocessing text."""
    text = "This is a sample text with stopwords and different forms."
    processed_text = preprocess_text(text)
    expected_text = "sampl text stopword differ form"  # Expected result after stemming and stopword removal
    assert processed_text == expected_text

def test_save_tfidf_values(db_connection):
    """Test saving TF-IDF values to the database."""
    documents = ["This is a test document.", "This document is a test."]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    wikipedia_movie_ids = [1, 2]
    save_tfidf_values(db_connection, tfidf_matrix, wikipedia_movie_ids)

    cur = db_connection.cursor()
    cur.execute("SELECT * FROM sparse_tfidf")
    rows = cur.fetchall()
    assert len(rows) > 0  # Ensure that some rows were inserted

def test_process_and_save_documents(db_connection):
    """Test processing and saving documents to the database."""
    cur = db_connection.cursor()
    cur.execute("CREATE TABLE plot_summaries (wikipedia_movie_id INTEGER, plot_summary TEXT)")
    cur.execute("INSERT INTO plot_summaries (wikipedia_movie_id, plot_summary) VALUES (1, 'This is a test document.')")
    cur.execute("INSERT INTO plot_summaries (wikipedia_movie_id, plot_summary) VALUES (2, 'This document is a test.')")
    db_connection.commit()

    process_and_save_documents(db_connection)

    cur = db_connection.cursor()
    cur.execute("SELECT * FROM sparse_tfidf")
    rows = cur.fetchall()
    assert len(rows) > 0  # Ensure that some rows were inserted
