# api/embedding.py
from sentence_transformers import SentenceTransformer, util
import config

try:
    embedding_model = SentenceTransformer(config.SENTENCE_EMBEDDING_MODEL_NAME)
    print(f"Load Embedding Model: '{config.SENTENCE_EMBEDDING_MODEL_NAME}'.")
except Exception as e:
    print(f"Failed Loading Embedding model: {e}")
    embedding_model = None

def generate_embedding(text):
    """텍스트를 임베딩 텐서로 변환"""
    if not embedding_model or not text:
        return None
    
    try:
        # convert_to_tensor=True 옵션으로 바로 텐서를 얻습니다.
        return embedding_model.encode(text, convert_to_tensor=True)
    except Exception as e:
        print(f"Embedding Failed: {e}")
        return None

def calculate_similarity(embedding1, embedding2):
    """두 임베딩 텐서 간의 코사인 유사도를 계산합니다."""
    if embedding1 is None or embedding2 is None:
        return 0.0
    
    return util.cos_sim(embedding1, embedding2).item()