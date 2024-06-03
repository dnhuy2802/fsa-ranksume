from qdrant_client import QdrantClient
from qdrant_client.http import models

import os
from dotenv import load_dotenv

load_dotenv()

qdrant_client = QdrantClient(
    url = os.getenv("RANKSUME_QDRANT_URL"), 
    api_key = os.getenv("RANKSUME_QDRANT_API_KEY"),
)
print("Qdrant Database connected")

# 2. Check if the question_tests exists
if qdrant_client.collection_exists('question_tests') == False:
    qdrant_client.create_collection(
    collection_name="question_tests",
    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
    )
    print("Collection question_tests created")
# 3. Check if the rag_documents_test exists
if qdrant_client.collection_exists('rag_documents_test') == False:
    qdrant_client.create_collection(
    collection_name="rag_documents_test",
    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
    )
    print("Collection rag_documents_test created")
# 4. Check if the jds exists
if qdrant_client.collection_exists('jds') == False:
    qdrant_client.create_collection(
    collection_name="jds",
    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
    )
    print("Collection jds created")
else:
    print("Collections already exist")
# 5. Check if the exams exists
if qdrant_client.collection_exists('exams') == False:
    qdrant_client.create_collection(
    collection_name="exams",
    vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
    )
    print("Collection exams created")
