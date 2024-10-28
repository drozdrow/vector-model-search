"""
Main file for the Vector Model Application
"""

import time
import tkinter as tk
import sqlite3
from tkinter import scrolledtext, ttk, font
from collections import defaultdict
import customtkinter as ctk
import numpy as np
from PIL import Image

def create_connection(db_file):
    """ Create a connection to a SQLite database """
    connection = None
    try:
        connection = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return connection

def search_movies(con, query):
    """ Search movies by title """
    cur = con.cursor()
    cur.execute("""SELECT movie_name,
                        movie_genres,
                        movie_release_date,
                        wikipedia_movie_id FROM movies
                        WHERE movie_name LIKE ?""",
                        ('%' + query + '%',))
    return cur.fetchall()

def load_initial_data(connection):
    """ Loading initial data """
    cur = connection.cursor()
    cur.execute("""SELECT movie_name,
                        movie_genres,
                        movie_release_date,
                        wikipedia_movie_id FROM movies
                        ORDER BY wikipedia_movie_id DESC
                        LIMIT 20""")
    return cur.fetchall()

def get_tfidf_vector(cur, wikipedia_movie_id):
    """ Get the TF-IDF vector for a specific movie """
    cur.execute("""SELECT tfidf_index, tfidf_value
                   FROM sparse_tfidf
                   WHERE wikipedia_movie_id=?""", (wikipedia_movie_id,))
    return cur.fetchall()

def calculate_norm(vector):
    """ Calculate the norm of a TF-IDF vector """
    return np.sqrt(sum(tfidf * tfidf for tfidf in vector.values()))

def calculate_similarities(current_vector, norm_current, all_vectors, current_movie_id):
    """ Calculate cosine similarities between the current movie and all other movies """
    similarities = defaultdict(float)
    norms = defaultdict(float)
    for movie_id, idx, tfidf in all_vectors:
        if movie_id != current_movie_id:
            norms[movie_id] += tfidf * tfidf
            if idx in current_vector:
                similarities[movie_id] += tfidf * current_vector[idx]
    for movie_id in similarities:
        norms[movie_id] = np.sqrt(norms[movie_id])
        similarities[movie_id] /= (norm_current * norms[movie_id])
    return similarities

def get_movie_names(cur, movie_ids):
    """ Get movie names for the given movie IDs """
    query_placeholders = ','.join(['?'] * len(movie_ids))
    cur.execute(f"""SELECT wikipedia_movie_id, movie_name
                    FROM movies
                    WHERE wikipedia_movie_id IN ({query_placeholders})""", movie_ids)
    return dict(cur.fetchall())

def find_similar_movies(connection, wikipedia_movie_id, top_n=5):
    """ Find similar movies based on TF-IDF """
    start_time = time.time()
    cur = connection.cursor()

    # Assembling the TF-IDF of the current movie into a sparse vector
    current_data = get_tfidf_vector(cur, wikipedia_movie_id)
    if not current_data:
        return []

    # Calculate the norm of the current movie
    current_vector = dict(current_data)
    norm_current = calculate_norm(current_vector)

    # Get the vectors of all other films
    cur.execute("SELECT wikipedia_movie_id, tfidf_index, tfidf_value FROM sparse_tfidf LIMIT 2000000")
    all_vectors = cur.fetchall()

    # Calculate similarity using scalar product
    similarities = calculate_similarities(current_vector, norm_current, all_vectors, wikipedia_movie_id)

    # Sort and select top N similar movies
    sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)[:top_n]

    # Getting movie titles for identifiers
    movie_ids = [movie_id for movie_id, _ in sorted_similarities]
    if movie_ids:
        movie_names = get_movie_names(cur, movie_ids)
        similar_movies_with_names = [(movie_names[movie_id], score)
                                     for movie_id, score in sorted_similarities
                                     if movie_id in movie_names]

        elapsed_time = time.time() - start_time  # End timing
        print(f"find_similar_movies() took {elapsed_time:.2f} seconds to execute")

        return similar_movies_with_names
    return []

def update_treeview(search_query):
    """ Updating Treeview with search results """
    for i in tree.get_children():
        tree.delete(i)
    if search_query:
        rows = search_movies(conn, search_query)
    else:  # If the request is empty, load the initial data
        rows = load_initial_data(conn)
    for row in rows:
        tree.insert('', tk.END, iid=row[3], values=row[:3])

def update_similar_movies_treeview(similar_movies):
    """ Update Treeview with similar movies with titles and similarity ratings """
    for i in similar_movies_tree.get_children():
        similar_movies_tree.delete(i)
    for movie_title, score in similar_movies:
        similar_movies_tree.insert('', tk.END, values=(f"{movie_title} (Similarity: {score:.2f})",))

def on_select(_event):
    """ Handling selection in Treeview """
    selected_item = tree.focus()
    if not selected_item:
        return

    cur = conn.cursor()
    query = "SELECT plot_summary FROM plot_summaries WHERE wikipedia_movie_id=?"
    cur.execute(query, (selected_item,))
    plot_summary = cur.fetchone()
    movie_details_text.delete('1.0', tk.END)

    if plot_summary:
        movie_details_text.insert(tk.INSERT, plot_summary[0])
        try:
            similar_movies_with_names = find_similar_movies(conn, int(selected_item))
            update_similar_movies_treeview(similar_movies_with_names)
        except sqlite3.DatabaseError as db_err:
            print(f"Database error when searching for similar movies: {db_err}")
            movie_details_text.insert(tk.END, "\nDatabase error retrieving similar movies.")
        except ValueError as val_err:
            print(f"Value error when searching for similar movies: {val_err}")
            movie_details_text.insert(tk.END, "\nValue error retrieving similar movies.")
    else:
        movie_details_text.insert(tk.INSERT, "No plot summary available for this movie.")

def on_similar_select(_event):
    """ Handling selection in the similar movies Treeview """
    selected_item = similar_movies_tree.focus()
    if not selected_item:
        return

def main():
    """Main function to initialize and run the application"""
    global tree, conn, movie_details_text, similar_movies_tree

    root = ctk.CTk()
    root.geometry('800x400')
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    # pylint: disable=W0212
    bg_color = root._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
    # pylint: enable=W0212
    custom_font = font.Font(family="Robotic", size=12)
    root.title('Movie Vector Model Application')

    style = ttk.Style()
    # pick a theme
    style.theme_use('default')
    style.configure("Treeview",
                    background=bg_color,
                    foreground="white",
                    rowheight=35,
                    fieldbackground=bg_color
                    )
    style.map('Treeview',
              background=[('selected', 'dark blue')])
    #film sheet
    columns = ('movie_name', 'movie_genres', 'movie_release_date')
    tree = ttk.Treeview(root, columns=columns, show='headings', height=20)
    tree.heading('movie_name', text='Title')
    tree.heading('movie_genres', text='Genre')
    tree.heading('movie_release_date', text='Release Date')
    tree.bind('<<TreeviewSelect>>', on_select)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    tree.column('movie_name', width=120, anchor='center')
    tree.column('movie_genres', width=120, anchor='center')
    tree.column('movie_release_date', width=100, anchor='center')

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    movie_details_text = scrolledtext.ScrolledText(root, height=10, font=custom_font)
    movie_details_text.pack(side=ctk.TOP,fill=tk.BOTH, expand=True)
    #input line
    search_var = ctk.StringVar()
    search_entry = tk.Entry(root, textvariable=search_var)
    search_entry.pack(side=ctk.BOTTOM, fill=tk.X)

    #button search
    img = ctk.CTkImage(Image.open(r"pictures/search_button.png"))
    search_button = ctk.CTkButton(root, text="Search", text_color='black',
                                  command=lambda: update_treeview(search_var.get()),
                                  image = img, corner_radius=0)
    search_button.pack(side=ctk.BOTTOM, fill=ctk.X)

    conn = create_connection('movies.db')
    for x in load_initial_data(conn):
        tree.insert('', tk.END, values=x)
    update_treeview('')

    # similar film sheet
    columns_similar = ('similar_movie_name',)
    similar_movies_tree = ttk.Treeview(root, columns=columns_similar, show='headings', height=5)
    similar_movies_tree.heading('similar_movie_name', text='Similar Titles')
    similar_movies_tree.bind('<<TreeviewSelect>>', on_similar_select)
    similar_movies_tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    similar_movies_tree.column('similar_movie_name', width=120, anchor='center')

    root.mainloop()

if __name__ == "__main__":
    main()
