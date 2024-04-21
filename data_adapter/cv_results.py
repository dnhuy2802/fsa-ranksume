from configs.mongodb import mongodb_client

class CvResults:
    def __init__(self, db_name="ranksume", collection_name="cv_results"):
        self.db = mongodb_client[db_name]
        self.collection = self.db[collection_name]

    def insert_one(self, data):
        return self.collection.insert_one(data)

    def insert_many(self, data):
        return self.collection.insert_many(data)

    def find_one(self, query):
        return self.collection.find_one(query)

    def find(self, query):
        return self.collection.find(query)

    def update_one(self, query, data):
        return self.collection.update_one(query, data)

    def update_many(self, query, data):
        return self.collection.update_many(query, data)

    def delete_one(self, query):
        return self.collection.delete_one(query)

    def delete_many(self, query):
        return self.collection.delete_many(query)