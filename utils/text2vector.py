import os
import voyageai

from dotenv import load_dotenv

# load the environment variables
load_dotenv()
# Define the google api key
os.environ['VOYAGE_API_KEY'] = os.getenv('VOYAGE_API_KEY')
VOYAGE_API_KEY = os.environ.get("VOYAGE_API_KEY")

vo = voyageai.Client(api_key=VOYAGE_API_KEY)

def text2vector(text: str):
    vector = vo.embed(text, model="voyage-2").embeddings[0]
    return vector
