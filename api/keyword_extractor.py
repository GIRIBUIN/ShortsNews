# api/keyword_extractor.py (개선 버전)
from kiwipiepy import Kiwi
from collections import Counter
import re

kiwi = Kiwi()

def extract_keywords(selected_article, similar_articles, original_keyword, num_keywords=5):
    """
    유사도 기반 가중치 + 복합 키워드 추출
    """
    # 원본 뉴스 강조 (2배 가중치)
    original_text = selected_article['summary'] * 2
    
    # 유사도 0.4 이상만 사용
    filtered_similar = [art for art in similar_articles if art.get('similarity', 0) >= 0.4]
    
    # 유사도 기반 가중치 적용
    weighted_texts = [original_text]
    for article in filtered_similar:
        similarity = article.get('similarity', 0)
        repeat_count = max(1, int(similarity * 3))
        summary_text = article.get('summary', "")
        weighted_texts.extend([summary_text] * repeat_count)
    
    combined_text = " ".join(weighted_texts)

    # 형태소 분석
    tokens = kiwi.tokenize(combined_text)
    nouns = [token.form for token in tokens 
             if token.tag in ['NNG', 'NNP'] 
             and len(token.form) > 1]
    
    # 불용어 제거
    stopwords = {'기자', '뉴스', '연합뉴스', '사진', '오전', '오후', '네이버뉴스', '향후',
                 '채널', '방송', '통신', '경제', '매체', '속보', '헤럴드', '일보', '신문', '닷컴', '때문',
                 '금일', '금주', '전날', '이번', '최근', '주가', '만원', '달러', '포인트', '대비', '기준', '이날',
                 '관련', '예정', '정부', '회의', '정책', '계획', '방안', '추진', '발표', '사업', '확대',
                 '대부분', '자체', '우리', '관계', '시작', '이후', '현재', '정도', '대한', '지난', '가장', '위해',
                 '지적', '처분', '평가', '기자'}  # 너무 일반적인 단어 추가
    
    pattern = re.compile(r'^[0-9\s]+$')
    
    filtered_nouns = [
        noun for noun in nouns
        if noun not in stopwords
        and original_keyword not in noun
        and not pattern.match(noun)
    ]
    
    # 빈도 계산
    counter = Counter(filtered_nouns)
    
    # 단일 키워드
    single_keywords = [word for word, _ in counter.most_common(num_keywords)]
    
    # 복합 키워드 생성
    compound_keywords = []
    for i in range(len(nouns) - 1):
        two_word = f"{nouns[i]} {nouns[i+1]}"
        if not any(stop in two_word for stop in stopwords):
            compound_keywords.append(two_word)
    
    compound_counter = Counter(compound_keywords)
    top_compounds = [kw for kw, _ in compound_counter.most_common(3)]
    
    # 결과 반환
    return {
        'single': single_keywords[:3],
        'compound': top_compounds[:2],
        'all': single_keywords + top_compounds
    }