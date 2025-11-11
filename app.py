from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import traceback
import math

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

def get_mongodb_connection():
    try:
        mongo_uri = os.getenv('MONGO_URI')
        database_name = os.getenv('MONGO_DATABASE')
        collection_name = os.getenv('MONGO_COLLECTION')

        if not mongo_uri or not database_name or not collection_name:
            raise ValueError("MongoDB connection parameters tidak lengkap")

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

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 200,
        'message': 'Backend Rekomendasi Skripsi Online'
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        collection = get_mongodb_connection()
        if collection is None:
            return jsonify({
                'status': 500, 
                'message': 'Gagal koneksi ke database'
            }), 500

        data = request.json or {}
        
        query = data.get('query', '').strip()
        category = data.get('category')
        year = data.get('year')
        page = data.get('page', 1)
        limit = data.get('limit', 10)

        mongo_query = {}

        if query:
            mongo_query['$text'] = {'$search': query}

        if category:
            mongo_query['Kategori'] = category

        if year:
            try:
                mongo_query['Tahun Terbit'] = int(year)
            except ValueError:
                pass

        total_results = collection.count_documents(mongo_query)
        total_pages = math.ceil(total_results / limit)

        skip = (page - 1) * limit
        
        results = list(
            collection.find(mongo_query)
            .sort('Tahun Terbit', -1)
            .skip(skip)
            .limit(limit)
        )

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

@app.route('/health', methods=['GET'])
def health_check():
    try:
        collection = get_mongodb_connection()
        if collection is None:
            return jsonify({
                'status': 500,
                'message': 'Database connection failed'
            }), 500
        
        return jsonify({
            'status': 200,
            'message': 'Backend sehat dan siap digunakan'
        })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Health check error: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
