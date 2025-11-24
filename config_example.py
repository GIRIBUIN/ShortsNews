# config.py

# YOUR_CLIENT_ID와 YOUR_CLIENT_SECRET을 실제 키로 대체하세요.
NAVER_CLIENT_ID = "NAVER_CLIENT_ID"
NAVER_CLIENT_SECRET = "NAVER_CLIENT_SECRET"

NEWS_COUNT = 10 # 뉴스 감성 분석에 사용할 기사 수

# 3. Hugging Face 모델 및 파라미터
KOBART_MODEL_NAME = 'gogamza/kobart-summarization'
SENTIMENT_MODEL_NAME = 'snunlp/KR-FinBert-SC'
SENTENCE_EMBEDDING_MODEL_NAME = "jhgan/ko-sroberta-multitask"

# KoBART 요약 파라미터 기본값
SUM_MAX_LEN = 130
SUM_MIN_LEN = 40
CHUNK_SIZE = 800
