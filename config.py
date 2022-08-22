class Config:
    JWT_SECRET_KEY = 'yh20220621##wherewegotowatch'  # 절대 노출시키면 안되는 키
    JWT_ACCESS_TOKEN_EXPIRES = False # True로 설정하면 3분의 유효기간이 생긴다.
    PROPAGATE_EXCEPTIONS = True # JWT가 예외처리를 해주는 옵션

    # KOPIS eyoo1
    KOPIS_ACCESS_KEY = '03222d0200ec47f88b472204636f002b'
    # 공연 조회
    KOPIS_PERFORMANCE_SERARCH_URL = 'http://kopis.or.kr/openApi/restful/pblprfr'
    # 공연 상세 조회
    KOPIS_PERFORMANCE_DETAIL_URL = 'http://kopis.or.kr/openApi/restful/pblprfr/' # 공연 아이디 기재
    # 공연 시설 조회
    KOPIS_PERFORMANCE_PLACE_SERACH_URL = 'http://kopis.or.kr/openApi/restful/prfplc'
    # 공연 시설 상세 조회
    KOPIS_PERFORMANCE_PLACE_DETAIL_URL = 'http://kopis.or.kr/openApi/restful/prfplc/' # 공연 시설 아이디 기재