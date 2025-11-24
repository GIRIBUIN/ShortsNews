from api.naver import get_naver_news, clean_text
from api.summary_ai import summarize_kobart_advanced
from api.embedding import generate_embedding, calculate_similarity
from api.keyword_extractor import extract_keywords

processed_articles = [] # 처리된 뉴스
current_keyword = "" # 

def process_keyword_search(keyword):
    """키워드로 뉴스를 검색 -> 뉴스 요약 -> 임베딩"""
    global processed_articles, current_keyword
    processed_articles = []
    current_keyword = keyword

    news_data = get_naver_news(keyword)
    if not (news_data and 'items' in news_data):
        print("Failed API")
        return False

    articles = news_data['items']
    for i, article_data in enumerate(articles):
        title = clean_text(article_data['title'])
        url = clean_text(article_data['originallink'])
        description = clean_text(article_data['description'])
        
        summary = summarize_kobart_advanced(description, max_len=100, min_len=30)
        embedding = generate_embedding(summary)

        processed_article = {
            'id': i + 1,
            'title': title,
            'url': url,
            'summary': summary,
            'embedding': embedding
        }
        processed_articles.append(processed_article)
        
        # UI 표시는 main에서 하도록 데이터를 반환하거나, 여기서 간단히 출력
        print(f"\n--- 뉴스 #{i+1} ---")
        print(f"제목: {title}")
        print(f"요약: {summary}")
        if embedding is None:
            print("Failed Embedding")

    return True

def get_article_list_for_display():
    """UI 표시를 위해 현재 처리된 뉴스 목록을 반환합니다."""
    return processed_articles

def find_and_recommend(selected_id, top_k=3):
    """유사 뉴스를 찾고 추천 검색어를 생성하여 반환합니다."""
    if not processed_articles:
        return None, "No News."

    selected_article = next((a for a in processed_articles if a['id'] == selected_id), None)
    if not selected_article:
        return None, f"ID '{selected_id}' is not here."
    if selected_article['embedding'] is None:
        return None, f"Selected News (ID: {selected_id}) does not have Embedding."

    # 유사도 계산
    similarities = []
    for article in processed_articles:
        if article['id'] == selected_id:
            continue
        similarity = calculate_similarity(selected_article['embedding'], article['embedding'])
        similarities.append({'article': article, 'similarity': similarity})

    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    top_similar_articles_with_sim = similarities[:top_k]
    
    # 키워드 추출
    recommended_keywords_dict = extract_keywords(
        selected_article, 
        top_similar_articles_with_sim, # 유사도 점수가 포함된 리스트 전달
        current_keyword
    )

    return {
        'selected': selected_article,
        'similar_articles': similarities[:top_k],
        'recommended_keywords': recommended_keywords_dict
    }, None