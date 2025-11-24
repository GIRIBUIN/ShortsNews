# main.py
import shorts_news # 우리의 컨트롤러를 임포트

def print_news_list():
    """현재 뉴스 목록을 출력합니다."""
    articles = shorts_news.get_article_list_for_display()
    if not articles:
        print("No News.")
        return
        
    print("\n--- Search News List ---")
    for article in articles:
        print(f"ID: {article['id']}, 제목: {article['title']}")

def run_console_app():
    """사용자 입력을 받아 앱을 실행하는 메인 루프입니다."""
    while True:
        print("\n--- Shorts News ---")
        print("1. 새 키워드로 뉴스 검색")
        print("2. 현재 검색된 뉴스 목록 보기")
        print("3. 유사 뉴스 찾기 및 키워드 추천")
        print("4. 종료")
        
        choice = input("Enter Mode (1-4): ")

        if choice == '1':
            search_keyword = input("Enter News Keywords: ")
            if shorts_news.process_keyword_search(search_keyword):
                print("\n뉴스 검색 및 처리 완료.")
                print_news_list()
        elif choice == '2':
            print_news_list()
        elif choice == '3':
            try:
                selected_id = int(input("Enter News ID: "))
                result, error_message = shorts_news.find_and_recommend(selected_id)

                if error_message:
                    print(error_message)
                    continue

                # 결과 출력
                print(f"\n--- 선택된 뉴스: '{result['selected']['title']}' ---")
                print("--- 유사한 뉴스 ---")
                for item in result['similar_articles']:
                    print(f"  ID: {item['article']['id']}, 제목: {item['article']['title']} (유사도: {item['similarity']:.4f})")
                
                keywords_dict = result['recommended_keywords']
                
                if keywords_dict and keywords_dict.get('all'):
                    print("\n[추천 검색어]")
                
                # 단일 키워드와 복합 키워드를 분리하여 더 보기 좋게 출력
                if keywords_dict.get('single'):
                    print(f"  - 단일 키워드: " + " ".join(f"'{k}'" for k in keywords_dict['single']))
                
                if keywords_dict.get('compound'):
                    print(f"  - 복합 키워드: " + " ".join(f"'{k}'" for k in keywords_dict['compound']))
                else:
                    # 추천 검색어가 없는 경우 메시지 출력
                    print("\n추천 검색어를 생성하지 못했습니다.")

            except ValueError:
                print("Invalid News ID(may be 1~10).")
        elif choice == '4':
            print("Terminate Program.")
            break
        else:
            print("Invalid Mode(1~4)")

if __name__ == "__main__":
    # 필요한 라이브러리 설치 안내 (최초 실행 시)
    try:
        import konlpy
    except ImportError:
        print("="*50)
        print("필수 라이브러리가 설치.")
        print("'pip install konlpy JPype1'")
        print("Java(JDK) 8")
        print("="*50)
    else:
        run_console_app()