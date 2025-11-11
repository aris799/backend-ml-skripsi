from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnection:
    def __init__(self, 
                 mongo_uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
                 database=os.getenv('MONGO_DATABASE', 'DBskripsi'),
                 collection=os.getenv('MONGO_COLLECTION', 'skripsi')):
        try:
            self.client = MongoClient(mongo_uri)
            self.db = self.client[database]
            self.collection = self.db[collection]
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def get_collection(self):
        return self.collection

    def close_connection(self):
        if self.client:
            self.client.close()
