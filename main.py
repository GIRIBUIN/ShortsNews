import torch
import matplotlib
import pandas
from transformers import pipeline

summarizer = pipeline("summarization", model="gogamza/kobart-base-v2")

# 2. 긴 뉴스 기사 텍스트 예시 (사용자 입력 대체 가능)
input_text = """(서울=뉴스1) 강민경 기자 = 다카이치 사나에 일본 총리가 대만 유사시 개입을 시사한 발언이 중일 갈등을 격화하는 상황에서 동아시아를 둘러싼 신냉전 구도가 더 첨예해졌다.

러시아와 북한이 중국과 한목소리를 내며 일본을 비판하는 가운데 미국과 대만은 일본을 지지하고 나서면서 아·태 지역에서 미국·일본·대만과 중국·러시아·북한의 대립 구도가 선명해졌다는 분석이 나온다.

일본을 서방 진영의 일부로 간주하는 러시아는 중국을 강하게 두둔했다. 러시아가 지배하고 있는 쿠릴 열도 남단 4개 섬에 대해 일본이 영유권을 주장해 양국간 영토 분쟁 문제도 있다.

중국 관영 글로벌타임스에 따르면 마리야 자하로바 러시아 외무부 대변인은 20일(현지시간) "80년이 지났는데도 일본은 국제법에 명시된 제2차 세계대전의 결과를 인정하지 않고 있다"며 "일본 정치인들이 역사를 이해하고 무책임한 발언이 무엇으로 이어지는지 알았으면 좋겠다"고 말했다."""

# 3. 요약 실행
summary_result = summarizer(
    input_text, 
    max_length=150,  # 최대 길이 설정
    min_length=30,   # 최소 길이 설정
    do_sample=False  # 확률 기반이 아닌 결정론적 결과 생성
)

print("--- 요약 결과 ---")
print(summary_result[0]['summary_text'])

