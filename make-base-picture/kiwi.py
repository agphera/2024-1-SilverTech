from kiwipiepy import Kiwi

"""
[시간 비교]
(공백 포함 80자)
base: 1.78s
sbg: 1.87s
typo: 9.41s

(공백 포함 401자)
base: 1.78s
sbg: 1.83s
typo: 9.76s

=> 시간상 typo는 절대 못쓸 것 같고, sbg 쪽으로 일단 시도
=> 추후에 완성되고, 발음 이슈로 인한 오타 문제가 심각하다면 typo 고려
"""

def base_noun_extractor(text):
    # 기본 모델
    kiwi = Kiwi()
    tokens = kiwi.tokenize(text, normalize_coda=True)

    results = set() # 중복 토큰 제거
    for token, pos, _, _ in tokens:
        if pos.startswith('NN'): # 일반 명사, 고유 명사, 의존 명사만 추출
            results.add(token)

    return results

def sbg_noun_extractor(text):
    # 먼 문단의 내용도 참고해 품사 태깅
    kiwi = Kiwi(model_type='sbg')
    tokens = kiwi.tokenize(text, normalize_coda=True)

    results = set() # 중복 토큰 제거
    for token, pos, _, _ in tokens:
        if pos.startswith('NN'): # 일반 명사, 고유 명사, 의존 명사만 추출
            results.add(token)

    return results

def typo_noun_extractor(text):
    # 오타 케어 (시간 오래걸림)
    kiwi = Kiwi(model_type='sbg', typos='basic')
    tokens = kiwi.tokenize(text, normalize_coda=True)

    results = set() # 중복 토큰 제거
    for token, pos, _, _ in tokens:
        if pos.startswith('NN'): # 일반 명사, 고유 명사, 의존 명사만 추출
            results.add(token)

    return results

if __name__ == "__main__":
    # # park1에 대한 설명을 음성 녹음 -> 한글 변환한 텍스트임. (조용한 환경에서 진행함)
    # test_text = "새가 날아다니고 꽃이 피어있네 옷을 길이 보이고 넘어예는 호수도 있구나 여러 나무들이 다양한 색으로 입을 펼쳤고 멀리 희미하게 산이 보이려 하네"
    
    test_text = "흥부전은 한국 문학에서 가장 유명한 고전 소설 중 하나이다. 이 소설은 형제간의 관계에 대한 이야기를 전달한다. 흥부전의 등장한 주인공은 두 명이 있다. 첫 번째 주인공은 잔인하고 이기적인 형 “놀부”라고 한다. 두 번째 주인공은 선하고 착한 동생 “흥부”라고 한다. 놀부는 흥부를 항상 괴롭힌다. 하지만 항상 침착한 흥부는 놀부에게 절대 화내지 않는다. 놀부가 무슨 말해도 흥부는 항상 듣고 무조건 순종했다. 시간이 지날 때 놀부와 흥부의 부모님이 돌아갈 때 놀부는 물려준 재산을 몽땅 독차지하고 흥부에게 한 푼도 주지 않았다. 또한 흥부를 집에서 쫓아냈다. 내가 흥부전은 흥미로운 한국 고전 문학이라고 생각하고 흥부전에 대한 비평문을 쓰기로 결정했다. 흥부전에 대한 비평문 쓰기로 선택한 이유는 총 세 번이 있다."
    
    # results = base_noun_extractor(test_text)
    results = sbg_noun_extractor(test_text)
    # results = typo_noun_extractor(test_text)

    print(results)