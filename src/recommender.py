import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .db import DatabaseConnection  # Relative import

class ThesisRecommender:
    def __init__(self, mongo_uri=None, database=None, collection=None):
        # Koneksi database
        self.db_connection = DatabaseConnection(mongo_uri, database, collection)
        
        # Ambil data dari MongoDB
        self.load_data()
        
        # Persiapkan TF-IDF Vectorizer
        self.prepare_vectorizer()

    def load_data(self):
        # Ambil data dari koleksi MongoDB
        cursor = self.db_connection.get_collection().find({})
        self.df = pd.DataFrame(list(cursor))
        
        # Preprocessing
        self.df['combined_text'] = self.df['title'] + ' ' + self.df.get('abstract', '') + ' ' + self.df.get('category', '')

    def prepare_vectorizer(self):
        # Inisialisasi TF-IDF Vectorizer
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['combined_text'])

    def recommend_titles(self, query='', category=None, year=None, limit=10):
        # Filter berdasarkan kategori dan tahun jika ada
        filtered_df = self.df.copy()
        
        if category:
            filtered_df = filtered_df[filtered_df['category'] == category]
        
        if year:
            filtered_df = filtered_df[filtered_df['year'] == year]

        # Jika query kosong, return berdasarkan filtering
        if not query:
            return filtered_df.head(limit)[['title', 'category', 'year']].to_dict('records')

        # Hitung similarity dengan query
        query_vector = self.tfidf.transform([query])
        cosine_similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # Gabungkan similarity dengan DataFrame
        filtered_df['similarity'] = cosine_similarities

        # Sort dan ambil top-k
        recommended = filtered_df.sort_values('similarity', ascending=False).head(limit)
        
        return recommended[['title', 'category', 'year', 'similarity']].to_dict('records')

    def __del__(self):
        # Tutup koneksi database saat objek dihapus
        self.db_connection.close_connection()
    