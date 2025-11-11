from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import traceback
import math

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Koneksi MongoDB
def get_mongodb_connection():
    try:
        mongo_uri = os.getenv('MONGO_URI')
        database_name = os.getenv('MONGO_DATABASE')
        collection_name = os.getenv('MONGO_COLLECTION')

        client = MongoClient(mongo_uri)
        db = client[database_name]
        collection = db[collection_name]
        
        # Buat indeks untuk pencarian
        collection.create_index([
            ('Judul Skripsi', 'text'),
            ('abstrak_bersih', 'text'),
            ('Penulis', 'text')
        ])
        
        return collection
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        return None

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Ambil koleksi MongoDB
        collection = get_mongodb_connection()
        if collection is None:
            return jsonify({
                'status': 500, 
                'message': 'Gagal koneksi ke database'
            }), 500

        # Terima payload dari frontend
        data = request.json or {}
        
        # Ekstrak parameter pencarian
        query = data.get('query', '').strip()
        category = data.get('category')
        year = data.get('year')
        page = data.get('page', 1)
        limit = data.get('limit', 10)

        # Bangun query MongoDB
        mongo_query = {}

        # Filter berdasarkan kata kunci (menggunakan abstrak_bersih untuk pencarian)
        if query:
            mongo_query['$text'] = {'$search': query}

        # Filter berdasarkan kategori
        if category:
            mongo_query['Kategori'] = category

        # Filter berdasarkan tahun
        if year:
            try:
                mongo_query['Tahun Terbit'] = int(year)
            except ValueError:
                pass

        # Hitung total results
        total_results = collection.count_documents(mongo_query)
        total_pages = math.ceil(total_results / limit)

        # Lakukan pencarian dengan pagination
        skip = (page - 1) * limit
        
        # Sorting berdasarkan tahun terbaru
        results = list(
            collection.find(mongo_query)
            .sort('Tahun Terbit', -1)
            .skip(skip)
            .limit(limit)
        )

        # Konversi ObjectId ke string dan normalisasi field
        processed_results = []
        for result in results:
            processed_result = {
                'judul': result.get('Judul Skripsi', 'Judul Tidak Tersedia'),
                'penulis': result.get('Penulis', 'Penulis Tidak Diketahui'),
                'tahun': str(result.get('Tahun Terbit', 'Tahun Tidak Tersedia')),
                'kategori': result.get('Kategori', 'Kategori Tidak Diketahui'),
                'abstrak': result.get('Abstrak', 'Tidak ada abstrak')
            }
            processed_results.append(processed_result)

        return jsonify({
            'status': 200,
            'total_results': total_results,
            'total_pages': total_pages,
            'current_page': page,
            'results': processed_results
        })

    except Exception as e:
        print(f"Search Error: {traceback.format_exc()}")
        return jsonify({
            'status': 500, 
            'message': f'Terjadi kesalahan dalam pencarian: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
