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

    # Aws
    AWS_ACCESS_KEY = 'AKIAWXNF62KJVP7HTOTC'
    AWS_SECRET_KEY = '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'

    # GOOGLE MAPS
    GOOGLE_API_KEY = 'AIzaSyDLRY2CF9QwQ5UENhzwJsOb6FKKqieCwhk'
    # GOOGLE MAPSS NearBySearch
    GOOGLE_MAP_NEAR_BY_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

    # S3 버킷이름과 기본 URL 주소 설정
    S3_BUCKET = 'prf-image-eyoo95'
    S3_LOCATION = 'https://prf-image-eyoo95.s3.ap-northeast-2.amazonaws.com/'