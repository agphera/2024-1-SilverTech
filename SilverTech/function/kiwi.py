from kiwipiepy import Kiwi

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