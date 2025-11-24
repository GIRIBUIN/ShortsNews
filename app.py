# app.py
import streamlit as st
import shorts_news # 우리가 만든 컨트롤러 임포트

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="AI 뉴스 요약 및 추천", page_icon="📰", layout="wide")

# --- 세션 상태 초기화 ---
if 'news_articles' not in st.session_state:
    st.session_state.news_articles = []
if 'selected_article_info' not in st.session_state:
    st.session_state.selected_article_info = None
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'keyword_to_search' not in st.session_state:
    st.session_state.keyword_to_search = ""
# [추가 1] 왼쪽 컬럼에서 활성화된 뉴스 ID를 저장하기 위한 상태
if 'active_news_id' not in st.session_state:
    st.session_state.active_news_id = None

# --- 콜백 함수 정의 ---

def request_search():
    if st.session_state.keyword_input:
        st.session_state.keyword_to_search = st.session_state.keyword_input
        st.session_state.processing = True
        st.session_state.news_articles = []
        st.session_state.selected_article_info = None
        st.session_state.active_news_id = None # 검색 시 활성화된 뉴스 초기화
    else:
        st.error("검색할 키워드를 입력해주세요.")

def request_history_load(keyword, articles):
    st.session_state.keyword_to_search = keyword
    st.session_state.news_articles = articles
    st.session_state.selected_article_info = None
    st.session_state.active_news_id = None # 히스토리 로드 시 초기화

def handle_news_selection(selected_id):
    """[수정] 뉴스 버튼 클릭 시, 왼쪽 토글 상태 업데이트 및 오른쪽 AI 분석 실행."""
    # 1. 왼쪽 컬럼의 토글 상태 업데이트
    # 이미 선택된 버튼을 다시 누르면 토글을 닫고, 아니면 새로 연다.
    if st.session_state.active_news_id == selected_id:
        st.session_state.active_news_id = None
    else:
        st.session_state.active_news_id = selected_id
        
    # 2. 오른쪽 컬럼의 AI 분석 실행
    with st.spinner("AI가 유사 뉴스와 추천 검색어를 생성 중입니다..."):
        result, error_message = shorts_news.find_and_recommend(selected_id)
        if error_message:
            st.error(error_message)
            st.session_state.selected_article_info = None
        else:
            st.session_state.selected_article_info = result

# --- UI 그리기 ---
st.title("📰 AI 기반 뉴스 요약 및 추천")
main_placeholder = st.empty()

# --- 사이드바 UI (변경 없음) ---
with st.sidebar:
    st.header("뉴스 검색")
    st.text_input("검색할 키워드를 입력하세요:", placeholder="예: 건국대, AIOT", key='keyword_input', disabled=st.session_state.processing)
    st.button("뉴스 검색", on_click=request_search, use_container_width=True, disabled=st.session_state.processing)
    st.divider()
    st.header("최근 검색 기록")
    if not st.session_state.search_history:
        st.caption("검색 기록이 없습니다.")
    else:
        for item in st.session_state.search_history:
            st.button(item['keyword'], key=f"history_{item['keyword']}", on_click=request_history_load, args=(item['keyword'], item['articles']), use_container_width=True, disabled=st.session_state.processing)

# --- 메인 화면 처리 ---
if st.session_state.processing:
    with main_placeholder.container():
        st.info(f"AI가 '{st.session_state.keyword_to_search}' 관련 뉴스를 검색하고 요약하는 중입니다...")
        with st.spinner("잠시만 기다려주세요..."):
            keyword = st.session_state.keyword_to_search
            is_success = shorts_news.process_keyword_search(keyword)
            if is_success:
                current_articles = shorts_news.get_article_list_for_display()
                st.session_state.news_articles = current_articles
                st.session_state.search_history = [item for item in st.session_state.search_history if item['keyword'] != keyword]
                st.session_state.search_history.insert(0, {'keyword': keyword, 'articles': current_articles})
                st.session_state.search_history = st.session_state.search_history[:5]
            else:
                st.session_state.news_articles = []
                st.session_state.search_error = "뉴스를 가져오는 데 실패했습니다."
    st.session_state.processing = False
    st.rerun()


elif st.session_state.news_articles:
    with main_placeholder.container():
        col1, col2 = st.columns([1.4, 1])
        with col1:
            st.subheader(f"'{shorts_news.current_keyword}' 관련 뉴스 검색 결과")
            st.info("아래 목록에서 뉴스를 클릭하면 원본 요약을 보고 상세 분석을 시작합니다.")
            
            # --- [수정 2] 뉴스 목록 버튼 루프에 expander 추가 ---
            for article in st.session_state.news_articles:
                st.button(f"[**{article['id']}번 뉴스**] {article['title']}", key=f"news_btn_{article['id']}", on_click=handle_news_selection, args=(article['id'],), use_container_width=True)
                
                # [핵심] 현재 활성화된 ID와 이 article의 ID가 일치할 때만 expander를 표시
                if st.session_state.active_news_id == article['id']:
                    with st.expander("네이버 원본 요약 보기"):
                        # 'description' 키를 사용하여 원본 요약 표시
                        st.caption(article.get('description', '원본 요약이 없습니다.'))

        with col2:
            st.subheader("상세 분석 및 AI 추천")
            if st.session_state.selected_article_info:
                result = st.session_state.selected_article_info
                
                # --- [수정 2] 원문 기사 링크 추가 ---
                st.success(f"선택된 뉴스: {result['selected']['title']}")
                st.markdown(f"**[🔗 원문 기사 보기]({result['selected']['url']})**") # 링크 추가
                with st.expander("요약 내용 보기"):
                    st.write(result['selected']['summary'])
                
                st.divider()
                st.subheader("🤖 AI가 찾은 유사 뉴스")
                if result['similar_articles']:
                    for item in result['similar_articles']:
                        st.markdown(f"**{item['article']['title']}** (유사도: {item['similarity']:.2f})")
                        st.markdown(f"**[🔗 원문 기사 보기]({item['article']['url']})**") # 링크 추가
                        with st.expander("요약 내용 보기"):
                            st.write(item['article']['summary'])
                else:
                    st.write("유사한 뉴스를 찾지 못했습니다.")
                
                st.divider()
                st.subheader("💡 AI 추천 검색어")
                keywords_dict = result['recommended_keywords']
                if keywords_dict and keywords_dict.get('all'):
                    all_keywords = keywords_dict.get('compound', []) + keywords_dict.get('single', [])
                    if all_keywords:
                        cols = st.columns(min(len(all_keywords), 5))
                        for i, keyword in enumerate(all_keywords[:5]):
                            with cols[i]:
                                if st.button(f"#{keyword}", key=f"rec_kw_btn_{keyword}"):
                                    st.session_state.keyword_input = keyword
                                    request_search()
                                    st.rerun()
                    else:
                        st.write("추천 검색어를 생성하지 못했습니다.")
                else:
                    st.write("추천 검색어를 생성하지 못했습니다.")
            else:
                st.info("왼쪽 뉴스 목록에서 기사를 클릭하여 분석을 시작하세요.")

elif st.session_state.get('search_error'):
    with main_placeholder.container():
        st.error(st.session_state.search_error)
        del st.session_state.search_error
        st.info("왼쪽 사이드바에서 다시 검색을 시도하세요.")
else:
    with main_placeholder.container():
        st.info("왼쪽 사이드바에서 검색을 시작하세요.")

