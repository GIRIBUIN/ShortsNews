import torch
import re
import kss
from transformers import PreTrainedTokenizerFast
from transformers import BartForConditionalGeneration
import config

KOBART_MODEL_NAME = config.KOBART_MODEL_NAME
try:
    KOBART_TOKENIZER = PreTrainedTokenizerFast.from_pretrained(KOBART_MODEL_NAME)
    KOBART_MODEL = BartForConditionalGeneration.from_pretrained(KOBART_MODEL_NAME)
except Exception as e:
    print(f"Error load KoBART : {e}")



def summarize_kobart_advanced(text, max_len=130, min_len=40):
    text = re.sub(r'\s+', ' ', text).strip()
    
    sentences = kss.split_sentences(text)
    
    encoded_chunks = []
    current_tokens = []
    
    for sent in sentences:
        ids = KOBART_TOKENIZER.encode(sent)
        if len(current_tokens) + len(ids) < 800:
            current_tokens += ids
        else:
            if current_tokens:
                encoded_chunks.append(current_tokens)
            current_tokens = ids
    
    if current_tokens:
        encoded_chunks.append(current_tokens)
    
    chunk_summaries = []
    
    # 청크별 요약 (개선된 파라미터)
    for chunk in encoded_chunks:
        input_ids = [KOBART_TOKENIZER.bos_token_id] + chunk + [KOBART_TOKENIZER.eos_token_id]
        summary_ids = KOBART_MODEL.generate(
            torch.tensor([input_ids]),
            max_length=max_len,
            min_length=min_len,
            num_beams=8,
            repetition_penalty=1.5,
            length_penalty=1.2,
            no_repeat_ngram_size=4,
            early_stopping=True
        )
        chunk_summaries.append(
            KOBART_TOKENIZER.decode(summary_ids[0], skip_special_tokens=True)
        )
    
    if len(chunk_summaries) == 1:
        return postprocess_summary(chunk_summaries[0])
    
    # 최종 결합 요약
    combined = " ".join(chunk_summaries)
    combined_ids = KOBART_TOKENIZER.encode(combined)
    final_ids = [KOBART_TOKENIZER.bos_token_id] + combined_ids + [KOBART_TOKENIZER.eos_token_id]
    
    final_summary_ids = KOBART_MODEL.generate(
        torch.tensor([final_ids]),
        max_length=max_len,
        min_length=min_len,
        num_beams=10,
        repetition_penalty=1.6,
        length_penalty=1.0,
        no_repeat_ngram_size=4,
        temperature=0.8,
        top_k=50,
        top_p=0.95,
        early_stopping=True
    )
    
    final_summary = KOBART_TOKENIZER.decode(final_summary_ids[0], skip_special_tokens=True)
    return postprocess_summary(final_summary)

def postprocess_summary(summary):
    sentences = kss.split_sentences(summary)
    complete_sentences = [s for s in sentences if s.endswith(('.', '!', '?', '다'))]
    return ' '.join(complete_sentences) if complete_sentences else summary


# =========================
# 테스트 케이스
# =========================

def test_summarization():
    print("="*60)
    print("KoBART 요약 테스트 시작")
    print("="*60 + "\n")
    
    # 테스트 1: 짧은 텍스트
    test1 = """
    인공지능 기술이 빠르게 발전하면서 다양한 산업 분야에 적용되고 있다.
    특히 자연어 처리 기술은 번역, 요약, 챗봇 등에서 큰 성과를 보이고 있다.
    앞으로 더 많은 혁신이 기대된다.
    """
    
    # 테스트 2: 중간 길이 텍스트
    test2 = """
    최근 발표된 연구에 따르면 기후 변화가 가속화되고 있으며, 
    이로 인해 전 세계적으로 이상 기후 현상이 증가하고 있다.
    과학자들은 탄소 배출을 줄이기 위한 즉각적인 조치가 필요하다고 경고한다.
    재생 에너지 사용 확대와 에너지 효율 개선이 핵심 해결책으로 제시되고 있다.
    각국 정부는 2050년까지 탄소 중립을 달성하기 위한 로드맵을 수립하고 있다.
    그러나 실행 속도가 목표에 미치지 못한다는 비판도 제기되고 있다.
    """
    
    # 테스트 3: 긴 텍스트 (청크 분할)
    test3 = """
    한국의 K-pop은 전 세계적으로 큰 인기를 끌고 있다.
    BTS, 블랙핑크 등의 그룹은 빌보드 차트에서 상위권을 차지하며 글로벌 팬층을 확보했다.
    K-pop의 성공 요인은 높은 퀄리티의 음악과 퍼포먼스, 그리고 소셜 미디어를 활용한 팬과의 소통이다.
    특히 유튜브와 틱톡 같은 플랫폼을 통해 전 세계 팬들과 실시간으로 연결된다.
    K-pop 산업은 한국 경제에도 큰 기여를 하고 있다.
    문화 콘텐츠 수출액이 매년 증가하며 한류 붐을 이끌고 있다.
    정부도 K-pop을 포함한 한류 콘텐츠 육성에 적극적으로 나서고 있다.
    해외 공연, 굿즈 판매, 스트리밍 수익 등 다양한 수익 모델이 개발되고 있다.
    앞으로 K-pop은 더욱 다양한 장르와 협업을 통해 발전할 것으로 전망된다.
    """

    test4 = """
    제목: A사, 폐배터리 재활용 기술 혁신으로 '친환경 에너지' 시장 선도

    최근 글로벌 에너지 시장은 기후 변화 대응을 위한 친환경 에너지 전환에 박차를 가하고 있습니다. 이러한 흐름 속에서 국내 기업 A사는 폐배터리 재활용 기술의 획기적인 발전을 발표하며 업계의 주목을 받고 있습니다. 기존의 폐배터리 처리 방식은 환경 오염과 높은 비용이라는 두 가지 문제를 동시에 안고 있었습니다. 하지만 A사가 개발한 **'순환형 습식 추출 기술(C-WET)'**은 리튬, 니켈, 코발트 등 핵심 원료의 회수율을 95% 이상으로 끌어올렸으며, 공정 과정에서 발생하는 폐기물과 에너지 소비량을 획기적으로 줄였습니다. A사 관계자는 "이 기술은 단순한 재활용을 넘어, 고갈되어 가는 광물 자원의 지속 가능한 순환 구조를 만드는 데 기여할 것"이라고 밝혔습니다. 이미 유럽과 북미 지역의 주요 배터리 제조사들과 공급 계약을 논의 중이며, 전문가들은 A사의 기술이 향후 5년 내 폐배터리 재활용 시장의 표준이 될 것으로 예측하고 있습니다. 이번 기술 혁신을 통해 A사는 환경 보호와 경제적 가치 창출이라는 두 마리 토끼를 잡았다는 평가를 받고 있습니다.
    """
    
    tests = [
        ("테스트 1: 짧은 텍스트", test1),
        ("테스트 2: 중간 길이 텍스트", test2),
        ("테스트 3: 긴 텍스트 (청크 분할)", test3),
        ("테스트 4: 친환경 에너지", test4)
    ]
    
    for i, (title, text) in enumerate(tests, 1):
        print(f"\n{title}")
        print("-" * 60)
        print(f"원본 길이: {len(text)} 글자")
        print(f"원본 텍스트:\n{text.strip()}\n")
        
        try:
            summary = summarize_kobart_advanced(text, max_len=130, min_len=40)
            print(f"요약 길이: {len(summary)} 글자")
            print(f"요약 결과:\n{summary}")
        except Exception as e:
            print(f"Failed Summary: {e}")
        
        print("=" * 60)
    


# =========================
# 메인 실행
# =========================

if __name__ == "__main__":
    test_summarization()