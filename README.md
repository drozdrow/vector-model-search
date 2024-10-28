# Vector Model Application

## Overview

This application implements a vector model for document search, specifically designed to search through a collection of movie plot summaries. It allows users to search for movies by title, view detailed plot summaries, and find similar movies based on TF-IDF vectors and cosine similarity.

## Dependencies

The application requires the following dependencies:

- Python 3.x
- `sqlite3`
- `nltk`
- `scikit-learn`
- `numpy`
- `tkinter` (included with Python)
- `customtkinter`
- `Pillow`

These dependencies can be installed using the `requirements.txt` file.

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://gitlab.fit.cvut.cz/BI-PYT/B232/drozddan.git
   cd drozddan
   ```
   
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Prepare the Database**:
   Ensure the movies.db SQLite database is set up and populated with necessary data. You can use the provided scripts to set up and clean the database.
   - **Setup Database**: Run the script to set up the database schema and populate it with data.
     ```bash
     python setup_database.py
     ```
   - **Cleanup Database**: Run the script to clean the database by removing movies without summaries.
     ```bash
     python cleanup_database.py
     ```
   - **Process JSON Data**: Run the script to convert and process JSON data into the required format.
     ```bash
     python json_script.py
     ```

4. **Process and Save Documents**: Run the script to process movie plot summaries and save TF-IDF vectors into the database.
   ```bash
   python vector_model.py
   ```
   
## Running the Application

To start the application, run:
```bash
python main.py
```

## Running Tests

The project includes tests to verify the functionality of the application. To run the tests, run:
```bash
pytest
```

## Author:
- Daniil Drozdov