# app.py
import streamlit as st
import shorts_news # 우리가 만든 컨트롤러 임포트

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="AI 뉴스 요약 및 추천",
    page_icon="📰",
    layout="centered", # [수정 1] 레이아웃을 'centered'로 변경하여 가독성 향상
)

# --- 세션 상태(Session State) 초기화 ---
if 'news_articles' not in st.session_state:
    st.session_state.news_articles = []
if 'selected_article_info' not in st.session_state:
    st.session_state.selected_article_info = None

# --- 콜백 함수 정의 ---
# [수정 2] 라디오 버튼 값이 바뀔 때마다 실행될 함수
def find_and_update_similar_news():
    # st.session_state.selected_radio_key를 통해 현재 선택된 라디오 버튼 값을 가져옴
    selected_title = st.session_state.selected_radio_key
    if selected_title:
        selected_id = int(selected_title.split(" - ")[0].replace("ID: ", ""))
        
        # 스피너를 여기에서도 사용하여 로딩 중임을 표시
        with st.spinner("AI가 유사 뉴스와 추천 검색어를 생성 중입니다..."):
            result, error_message = shorts_news.find_and_recommend(selected_id)
            if error_message:
                st.error(error_message)
                st.session_state.selected_article_info = None # 오류 발생 시 이전 정보 초기화
            else:
                st.session_state.selected_article_info = result

# --- UI 그리기 ---

# 1. 제목
st.title("📰 AI 기반 뉴스 요약 및 추천")
st.write("관심있는 키워드를 입력하면 뉴스를 요약하고, 선택한 뉴스와 비슷한 뉴스를 추천해줍니다.")

# 2. 사이드바 (입력 공간)
with st.sidebar:
    st.header("뉴스 검색")
    search_keyword = st.text_input("검색할 키워드를 입력하세요:", placeholder="예: 수능, 반도체")

    if st.button("뉴스 검색", use_container_width=True):
        st.session_state.news_articles = []
        st.session_state.selected_article_info = None
        
        if search_keyword:
            with st.spinner("AI가 뉴스를 검색하고 요약하는 중입니다... 잠시만 기다려주세요."):
                is_success = shorts_news.process_keyword_search(search_keyword)
                if is_success:
                    st.session_state.news_articles = shorts_news.get_article_list_for_display()
                else:
                    st.error("뉴스를 가져오는 데 실패했습니다. API 키를 확인하거나 다른 키워드를 시도해보세요.")
        else:
            st.warning("검색어를 입력해주세요.")

# 3. 메인 화면 (결과 출력 공간)
if st.session_state.news_articles:
    # [수정 3] 컬럼(st.columns) 레이아웃 제거
    st.subheader(f"'{shorts_news.current_keyword}' 관련 뉴스 검색 결과")
    st.info("아래 목록에서 뉴스를 선택하면 바로 유사 뉴스를 찾아줍니다.")
    
    article_titles = [f"ID: {article['id']} - {article['title']}" for article in st.session_state.news_articles]
    
    # [수정 4] 라디오 버튼에 key와 on_change 콜백 함수 연결
    st.radio(
        "뉴스 목록:",
        article_titles,
        key='selected_radio_key', # 이 key를 통해 선택된 값에 접근
        on_change=find_and_update_similar_news, # 선택이 바뀔 때마다 이 함수 실행
        label_visibility="collapsed"
    )
    
    # [수정 5] 버튼을 제거하고, 세션 상태에 결과가 있으면 바로 출력
    if st.session_state.selected_article_info:
        result = st.session_state.selected_article_info
        
        # --- 결과 출력 부분 (이제 아래쪽에 순차적으로 표시됨) ---
        st.divider() # 구분선 추가
        st.success(f"선택된 뉴스: '{result['selected']['title']}'")
        
        with st.expander("요약 내용 보기"):
            st.write(result['selected']['summary'])
        
        st.subheader("🤖 AI가 찾은 유사 뉴스")
        if result['similar_articles']:
            for item in result['similar_articles']:
                st.markdown(f"**{item['article']['title']}** (유사도: {item['similarity']:.2f})")
                with st.expander("요약 내용 보기"):
                    st.write(item['article']['summary'])
        else:
            st.write("유사한 뉴스를 찾지 못했습니다.")

        st.subheader("💡 AI 추천 검색어")
        keywords_dict = result['recommended_keywords']
        if keywords_dict and keywords_dict.get('all'):
            if keywords_dict.get('compound'):
                st.markdown("##### 복합 키워드")
                st.write(" ".join(f"`{k}`" for k in keywords_dict['compound']))
            if keywords_dict.get('single'):
                st.markdown("##### 단일 키워드")
                st.write(" ".join(f"`{k}`" for k in keywords_dict['single']))
        else:
            st.write("추천 검색어를 생성하지 못했습니다.")