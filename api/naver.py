import os
import sys
import urllib.request
import requests
from bs4 import BeautifulSoup
import html
import json
import config

CLIENT_ID = config.NAVER_CLIENT_ID
CLIENT_SECRET = config.NAVER_CLIENT_SECRET
NEWS_COUNT = config.NEWS_COUNT


def clean_text(text):
    """ HTML 구조 정리 """
    soup = BeautifulSoup(text, 'html.parser')
    clean_text = soup.get_text()
    clean_text = html.unescape(clean_text)
    return clean_text

def get_naver_news(keyword):
    """ keyword로 검색한 네이버 뉴스 JSON 형태로 반환 """
    enc_text = urllib.parse.quote(keyword)
    # 뉴스 검색 API 엔드포인트 사용: /v1/search/news
    url = f"https://openapi.naver.com/v1/search/news?query={enc_text}&display={NEWS_COUNT}&sort=date"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)

    soup = BeautifulSoup(response.text, 'html.parser')


    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        
        if rescode == 200:
            response_body = response.read()
            return json.loads(response_body.decode('utf-8'))
        else:
            print(f"Error Code: {rescode}")
            return None
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        return None
    
if __name__ == "__main__":
    news_data = get_naver_news('이재명')

    if news_data and 'items' in news_data:
        articles = news_data['items']
        
        for i, article in enumerate(articles):
            title = clean_text(article['title'])
            url = clean_text(article['originallink'])
            link = clean_text(article['link'])
            description = clean_text(article['description'])


            print(f"\n=======================================================")
            print(f"뉴스 #{i+1} : {title}")
            print(f"url : {url}")
            print(f"link : {link}")
            # print(f"본문 : {}")
            print(f"원본 요약: {description}")
            print(f"=======================================================")
    else:
        print("뉴스를 찾을 수 없거나 API 호출에 실패했습니다.")