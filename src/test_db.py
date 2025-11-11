from dotenv import load_dotenv
from pymongo import MongoClient
import os

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    try:
        # Ambil URI dari .env
        mongo_uri = os.getenv('MONGO_URI')
        
        # Buat koneksi
        client = MongoClient(mongo_uri)
        
        # Cek koneksi
        client.admin.command('ismaster')
        
        # Print database yang tersedia
        print("Databases:", client.list_database_names())
        
        print("✅ Koneksi MongoDB Berhasil!")
        return True
    except Exception as e:
        print(f"❌ Koneksi Gagal: {e}")
        return False

# Jalankan tes
if __name__ == '__main__':
    test_mongodb_connection()
