import streamlit as st
import shorts_news  # 기존 컨트롤러 유지

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="AI 뉴스 요약 및 추천", page_icon="📰", layout="wide")

# --- 커스텀 CSS (UI 개선) ---
st.markdown("""
<style>
    .stButton button {
        text-align: left;
        display: block;
        width: 100%;
    }
    div[data-testid="stExpander"] details summary p {
        font-weight: 600;
    }
    .active-news {
        border: 2px solid #ff6464;
        border-radius: 5px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

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
if 'active_news_id' not in st.session_state:
    st.session_state.active_news_id = None

# --- 콜백 함수 정의 ---

def request_search():
    """검색 버튼 클릭 시 실행"""
    if st.session_state.keyword_input:
        st.session_state.keyword_to_search = st.session_state.keyword_input
        st.session_state.processing = True
        st.session_state.news_articles = []
        st.session_state.selected_article_info = None
        st.session_state.active_news_id = None
    else:
        st.error("검색할 키워드를 입력해주세요.")

def request_history_load(keyword, articles):
    """검색 기록 클릭 시 실행"""
    st.session_state.keyword_to_search = keyword
    st.session_state.keyword_input = keyword  # 입력창 동기화
    st.session_state.news_articles = articles
    st.session_state.selected_article_info = None
    st.session_state.active_news_id = None

def handle_news_selection(selected_id):
    """뉴스 목록 클릭 시 토글 및 분석 실행"""
    # 토글 로직
    if st.session_state.active_news_id == selected_id:
        st.session_state.active_news_id = None # 닫기
    else:
        st.session_state.active_news_id = selected_id # 열기
        
        # AI 분석 실행 (새로 열 때만)
        with st.spinner("🔍 AI가 분석 및 유사도를 계산하고 있습니다..."):
            result, error_message = shorts_news.find_and_recommend(selected_id)
            if error_message:
                st.toast(error_message, icon="⚠️") # 에러를 토스트 메시지로 변경
                st.session_state.selected_article_info = None
            else:
                st.session_state.selected_article_info = result

def apply_recommendation(keyword):
    st.session_state.keyword_input = keyword
    request_search()

# --- UI ---

# 헤더
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("📰 AI 기반 뉴스 요약 및 추천")
with col_h2:
    if st.session_state.keyword_to_search:
        st.caption(f"Current Keyword: **{st.session_state.keyword_to_search}**")

main_placeholder = st.empty()

# --- 사이드바 UI ---
with st.sidebar:
    st.header("🔍 뉴스 검색")
    st.text_input(
        "검색 키워드", 
        placeholder="예: 건국대, AIOT", 
        key='keyword_input', 
        disabled=st.session_state.processing,
        on_change=request_search
    )
    
    st.button(
        "▶️ 뉴스 검색 ◀️", 
        on_click=request_search, 
        use_container_width=True, 
        disabled=st.session_state.processing
    )
    
    st.divider()
    st.subheader("🕒 히스토리")
    if not st.session_state.search_history:
        st.caption("검색 기록이 없습니다.")
    else:
        for item in st.session_state.search_history:
            st.button(
                f"📄 {item['keyword']}", 
                key=f"history_{item['keyword']}", 
                on_click=request_history_load, 
                args=(item['keyword'], item['articles']), 
                use_container_width=True, 
                disabled=st.session_state.processing
            )

# --- 메인 화면 처리 ---

# 1. 처리 중일 때 (로딩 화면)
if st.session_state.processing:
    with main_placeholder.container():
        st.info(f"🤖 AI가 '{st.session_state.keyword_to_search}' 관련 뉴스를 분석 중입니다...")
        with st.spinner("뉴스를 수집하고 요약하는 중... 잠시만 기다려주세요."):
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
                st.session_state.search_error = "뉴스를 가져오는 데 실패했습니다. 키워드를 변경해 보세요."
    
    st.session_state.processing = False
    st.rerun()

# 2. 결과 화면
elif st.session_state.news_articles:
    with main_placeholder.container():
        # 왼쪽: 뉴스 목록 / 오른쪽: 상세 분석
        col1, col2 = st.columns([1.2, 1], gap="medium")
        
        # --- 좌측 뉴스 목록 ---
        with col1:
            st.subheader(f"📢 '{shorts_news.current_keyword}' 뉴스 목록")
            st.caption("뉴스를 클릭하면 AI 상세 분석이 시작됩니다.")
            
            for article in st.session_state.news_articles:
                is_active = st.session_state.active_news_id == article['id']
                
                # 활성화된 뉴스는 테두리로 강조
                container_border = is_active
                with st.container(border=container_border):
                    btn_icon = "✅" if is_active else "📰"
                    btn_label = f"{btn_icon} {article['title']}"
                    
                    st.button(
                        btn_label, 
                        key=f"news_btn_{article['id']}", 
                        on_click=handle_news_selection, 
                        args=(article['id'],), 
                        use_container_width=True,
                        type="primary" if is_active else "secondary"
                    )
                    
                    # 활성화된 경우 원본 요약(Description)
                    if is_active:
                        st.info("📌 **Naver 원본 요약**")
                        st.write(article.get('description', '요약 내용이 없습니다.'))
                        
        # --- 우측 AI 분석 결과 ---
        with col2:
            st.subheader("🧠 AI 상세 분석")
            
            if st.session_state.selected_article_info:
                result = st.session_state.selected_article_info
                selected_news = result['selected']

                tab1, tab2, tab3 = st.tabs(["📄 핵심 요약", "⚖️ 유사 뉴스", "💡 추천 검색어"])
                
                # [Tab 1] 선택된 뉴스 요약
                with tab1:
                    st.success(f"**{selected_news['title']}**")
                    st.markdown(f"🔗 **[원문 기사 보러가기]({selected_news['url']})**")
                    st.divider()
                    st.markdown("#### 📝 AI 3줄 요약")
                    st.write(selected_news['summary'])

                # [Tab 2] 유사 뉴스
                with tab2:
                    if result['similar_articles']:
                        st.info(f"유사도가 높은 뉴스 {len(result['similar_articles'])}건을 찾았습니다.")
                        for idx, item in enumerate(result['similar_articles']):
                            with st.expander(f"{idx+1}. {item['article']['title']} ({item['similarity']:.0%})"):
                                st.write(item['article']['summary'])
                                st.markdown(f"[🔗 기사 읽기]({item['article']['url']})")
                    else:
                        st.warning("유사한 뉴스를 찾지 못했습니다.")

                # [Tab 3] 추천 검색어
                with tab3:
                    st.write("이 뉴스와 관련된 추천 키워드입니다. 클릭 시 재검색합니다.")
                    keywords_dict = result['recommended_keywords']
                    
                    if keywords_dict and (keywords_dict.get('compound') or keywords_dict.get('single')):
                        all_keywords = keywords_dict.get('compound', []) + keywords_dict.get('single', [])
                        
                        # 키워드를 태그 형태로 나열
                        st.markdown("---")
                        # 가로로 여러 개 배치
                        k_cols = st.columns(3)
                        for i, keyword in enumerate(all_keywords[:9]): # 최대 9개까지만
                            with k_cols[i % 3]:
                                st.button(
                                    f"#{keyword}", 
                                    key=f"rec_{keyword}_{i}", 
                                    on_click=apply_recommendation, 
                                    args=(keyword,),
                                    use_container_width=True
                                )
                    else:
                        st.caption("추천 검색어를 생성할 수 없습니다.")
            
            else:
                # 선택된 뉴스가 없을 때의 안내 메시지
                with st.container(border=True):
                    st.markdown("""
                    ### 👋 분석 대기 중
                    검색한 뉴스 목록에서 관심 있는 기사를 클릭해주세요.
                    
                    **AI가 수행하는 작업:**
                    - 📄 뉴스 본문 상세 요약
                    - 🔗 내용이 유사한 다른 언론사 뉴스 검색
                    - 💡 더 깊이 알아볼 수 있는 키워드 추천
                    """)

elif st.session_state.get('search_error'):
    with main_placeholder.container():
        st.error(st.session_state.search_error)
        st.button("다시 시도", on_click=lambda: st.session_state.pop('search_error'), type="primary")

else:
    with main_placeholder.container():
        st.info("👈 왼쪽 사이드바에서 키워드를 입력하여 뉴스 검색을 시작하세요!")