from configs.qdrant_db import qdrant_client, models

class QdrantDb:
    def __init__(self, collection_name: str):
        self.qdrant_client = qdrant_client
        self.collection_name = collection_name
        self.collection_info = qdrant_client.get_collection(collection_name)
        self.models_qdrant = models

    # upsert points
    def upsert_points(self, points):
        return self.qdrant_client.upsert(collection_name=self.collection_name, points=points)
    
    # Delete corresponding vector from Qdrant
    def delete_corresponding_vector(self, points_selector):
        print(points_selector)
        return self.qdrant_client.delete(collection_name=self.collection_name, points_selector=points_selector)