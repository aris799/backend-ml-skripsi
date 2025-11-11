from src.db import get_mongodb_connection
from src.recommender import ThesisRecommender

def test_recommender():
    # Ambil koneksi database
    collection = get_mongodb_connection()
    
    # Inisiasi recommender
    recommender = ThesisRecommender(collection)
    
    # Contoh query
    query = "desain interaksi teknologi pendidikan"
    
    # Dapatkan rekomendasi
    results = recommender.recommend(query)
    
    # Tampilkan hasil
    print("Rekomendasi Skripsi:")
    for idx, result in enumerate(results, 1):
        print(f"{idx}. {result.get('Judul Skripsi', 'Judul Tidak Tersedia')}")

# Jalankan tes
if __name__ == '__main__':
    test_recommender()
