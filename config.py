class Config:
    JWT_SECRET_KEY = 'yh20220621##wherewegotowatch'  # 절대 노출시키면 안되는 키
    JWT_ACCESS_TOKEN_EXPIRES = False # True로 설정하면 3분의 유효기간이 생긴다.
    PROPAGATE_EXCEPTIONS = True # JWT가 예외처리를 해주는 옵션

    # KOPIS eyoo1
    KOPIS_ACCESS_KEY = '03222d0200ec47f88b472204636f002b'