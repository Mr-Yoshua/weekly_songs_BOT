from pymongo import MongoClient

class MongoDBManager:
    def __init__(self, url):
        self.client = MongoClient(url)
        self.db = self.client["weekly_songs"]
        self.collection = self.db["songs"]

    def insert_song(self, song_data):
        self.collection.insert_one(song_data)

    def get_songs(self):
        return self.collection.find()
    
    def get_song_by_name(self, name):
        return self.collection.find_one({"nombre": name})
    
    def update_song(self, song_data):
        self.collection.update_one({"nombre": song_data["nombre"]}, {"$set": song_data})
    
    def get_song_by_priority(self, priority):
        return self.collection.find({"priority": priority})
    
    def get_songs_by_classification(self, classification):
        return self.collection.find({"clasification": classification})
    
    def collection_has_data(self):
        return self.collection.count_documents({}) > 0

def connect_to_mongo(url):
    return MongoDBManager(url)