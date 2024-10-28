"""
This script sets up and populates a database with TF-IDF values from movie plot summaries.
It performs the following tasks:
1. Connects to a SQLite database.
2. Sets up a table to store sparse TF-IDF vectors, specifically storing non-zero TF-IDF values along with their indices.
3. Processes the text data from movie plot summaries by tokenizing, removing stopwords, and applying stemming.
4. Converts the preprocessed text data into TF-IDF vectors using the sklearn TfidfVectorizer.
5. Saves these sparse TF-IDF vectors into the database for later retrieval and analysis.
This script is designed to facilitate quick access to precomputed TF-IDF vectors for movie recommendation or search functionalities.
"""

import sqlite3
import time
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Ensure necessary NLTK resources are downloaded
#nltk.download('punkt')
#nltk.download('stopwords')


def setup_database(conn):
    """ Setup the database """
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS sparse_tfidf;")
    cur.execute("""
        CREATE TABLE sparse_tfidf (
            wikipedia_movie_id INTEGER,
            tfidf_index INTEGER,
            tfidf_value REAL,
            PRIMARY KEY (wikipedia_movie_id, tfidf_index)
        )
    """)
    # Indexes to speed up queries
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sparse_movie ON sparse_tfidf(wikipedia_movie_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sparse_index ON sparse_tfidf(tfidf_index);")
    conn.commit()

def create_connection(db_file):
    """ Create a connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn


def preprocess_text(text):
    """
    Tokenize, remove stop words, and apply stemming to the text.
    """
    # Initialize NLTK tools
    ps = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    processed_tokens = [ps.stem(w.lower())
                        for w in tokens
                        if w.lower()
                        not in stop_words and w.isalpha()]
    return ' '.join(processed_tokens)


def save_tfidf_values(conn, tfidf_matrix, wikipedia_movie_ids):
    """Save the TF-IDF values to the database"""
    cur = conn.cursor()
    data_to_insert = []
    for i, movie_id in enumerate(wikipedia_movie_ids):
        indices = tfidf_matrix[i].nonzero()[1]
        for idx in indices:
            value = tfidf_matrix[i, idx]
            data_to_insert.append((movie_id, idx, value))

    cur.executemany("""INSERT INTO sparse_tfidf
                        (wikipedia_movie_id,
                        tfidf_index,
                        tfidf_value)
                        VALUES (?, ?, ?)""",
                        data_to_insert)
    conn.commit()


def process_and_save_documents(conn):
    """Process and save the documents to the database"""
    cur = conn.cursor()
    cur.execute("SELECT wikipedia_movie_id, plot_summary FROM plot_summaries")
    wikipedia_movie_ids, documents = zip(*[(row[0],
                                        preprocess_text(row[1]))
                                        for row in cur.fetchall()])
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    save_tfidf_values(conn, tfidf_matrix, wikipedia_movie_ids)


def main():
    """main function to execute the script"""
    start_time = time.time()

    conn = create_connection('movies.db')
    #setup_database(conn)  # Ensure the database is setup
    process_and_save_documents(conn)  # Process and save documents
    conn.close()

    end_time = time.time()
    print(f"Execution completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
