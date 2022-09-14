# 공연 조회 API 서버 (뭐보러갈래) Overview
- 공연 정보와 내 지역의 공연 정보를 확인 할 수 있습니다.
- 사용자 기반 협업 필터링을 활용한 추천 인공지능으로 사용자들의 활동 패턴을 확인하고 좋아 할 것 같은 공연을 추천하는 기능을 포함하고 있습니다.
- 공연 티켓 이미지를 업로드하면 이미지의 글자를 판독하여 해당 공연과 일치하는 공연 티켓인지 확인하는 인공지능 기능을 포함하고 있습니다.
- 보안을 위해 환경 설정 파일 'config.py', 'mysql_connection.py' 파일은 포함되지 않아 깃허브의 파일만으로는 정상적인 실행이 되지 않음을 알려드립니다.

# GitHub
[PerformanceSearchAPI GitHub](http://)

# Repository File Structure
![file_dir](https://lh3.googleusercontent.com/fife/AAbDypB6cb1nIns0o3rrWIdfr7Tj9jTTEphaMuTlrMXVpV9T66DwOOt0tD-KVN65slZw_WYx57gHXxrfufGp-OpH5lUL2zGM92wzGVCmuDWqMUIUCVFt9slGEWGcihQ_idU91qGfBvj_TdKD8Jys64NLNQHuzpiqKxmn_Afak7gbN5P5t-Af3sKhaGxitGCvVV2ls0G1219MwvOtE5BQYFATkCZsNckQaqLEju0shk1DNTeWLQFNvROZ0uNE-jZCUIjMwRXPG0Amzbt-3OTLqw-KTkO4JP27dYha5_wkYVDqQEoxRUMwMcbl4_QHJ8VYJXVWhMRampI9dgpLR852c41yCVK9KpjQ4CxaUL6NLwUkJK_7EILYzFh8gZ2RlXvChaF0kPh9ovbHtd-hsMrtU73xJZjAkqR82ONImIUvELC3yoSmSXwVdtgN8vN6BIQ2KI4uIrLW9ILVUL9QPo0Hwn7dAT8DctwC5bKV6RuOHJC1iXd5T74W5kIuSZiOn7VcyiCCt9anzymU6Wf78hlXOLpQHqg5houk5wyOOyAuh0LFVNfnzFsYHsQBb96HS4GijUm_hx3Sc1gIAQ14SWuqB0s-XoBML9J2d4Df0vQ72kHFS7TBQvE77YuguwQPw7XzMcjkVyzcFhunZOjC7HnHzFJb77PUZqGVFhBiwyPwIxg8Uv_JIXImXuowdP-yfUdMtrTwrWxvMwgzsX07z2omXwNs8lhREiJ90rJHVRWe6zfFSdIKdSfv3qbaJuAeBsIzlXGYs3HiH7oKbTrfavbXmLAj2aPfyEAa5hRBBb9_bmnIE-08XWbmlqVtQi16S127abOo9JxyPZLhgDfs5ZYHOidEOvOk1DzclzMVINfJXkWvyeKDQ0UYK131ecu572WUEpZ1g5ijYn6RMVh5brrx2ZYXy28I7kkVJGh3havlOhQZhNhCS7sPc_IdBB7bzXDrZVxOBkzP6IjmVCdPgQw8RQGbrfmnc3PnckxSIqararx--sty6xqtFNz3mNeF23n18KnIdP-Fr_57ZVjSFSX7yOazXEUP8uXNMNCR8BLmAcRabhZgtXm3h3ITDVv0WB9C4AacNbAdq2S7Sv-1kh6idm8GFf1jfW4SbE24M_vFhJC590h0S1EQr37W4KHra0dqjdu6PbBtphRxNr6rLL5Cpte0XZUw4hDGd4b0vjoLOARMNK3TxX0CPnJJAhcW20ZmzKc7f9QfxM0ucwo2MzuyqEI4xVQScEilWwyfxxPU4mwvrlDsNO5-o1LLiyUcOHfrkDHvNy0MfqsNTA=w1335-h868)

### **메인**
- app.py : 실행을 위한 메인 flask api 서버 파일
### **환경 설정**
  - config.py : API 서버를 구성하기 위한 환경 설정 파일
  - mysql_connection.py : DB 환경 설정 파일
  - utils.py : 사용자 비밀번호 암호화 설정 파일
### **API 리소스**
  - resources 폴더 : 앱 실행시 필요한 추가 리소스 파일
    - clovaocr.py : 사용자로부터 업로드된 티켓 이미지를 해당 공연과 일치하는지 인공지능이 확인하는 기능
    - party.py : 사용자 간의 실시간 상호작용을 위한 기능(앱에서의 실시간 채팅 시스템을 위함)
    - performance.py : 공연 정보 관련 기능
    - posting.py : 자유 게시판 관련 기능
    - recommend.py : 사용자들 간의 비슷한 취향을 분석하여 인공지능이 개개인에 맞춰 공연을 추천해주는 기능
    - review.py : 공연의 리뷰 관련 기능
    - user.py : 회원 관련 기능
    
# Pre-requisite
### Library
- ##### 아래의 라이브러리가 설치되지 않을 경우 제대로 작동하지 않습니다.
  - pip install LibraryString
``` phtyon
flask-restful
Flask-JWT-Extended
requests
mysql-connector-python
psycopg2-binary
passlib
email-validator
xmltodict
boto3
time
datetime
uuid
json
pandas
```

# Api Function References
![file_dir](https://lh3.googleusercontent.com/fife/AAbDypBI6NCSweStGoFe2pvdK7WvQ_fjKLbKvalHnV0p-j0WdexjbQCWoB42ZcCUe0hxtrZhfnF4CociuetndBjsPMvKeHNA_OuZ589KkgZWmposIdQwgsZO7ZLUmmThC9abkVe7QTDccCrS6pIwphJTMjD8NSSArCMJROft1vAgsXMqNqVLFtYNGq2nMt6OzciDLnPbbzeBPPyq_voYNeL-UN_VGLyD0dfK0hxoFP5u9EU3NseeWsGig3Lg48r7poladgvcguHraPn-M8Uy0V_TXMh6hVKqMWLGdZvk8rE3Cm0GiKwkwA_u6_trVr-bIYwrTjpzjEfU5wvzwdhnLVLLxCzGwvQD148a0l4t7mIxkjLn-Y4HOTk-N0pfJskxTTWx6sKoydLQ2JlzS1DaAp6omSxUBjPTQrCoMwVF4iBRNA1bmAT3Ccy24zhNw4W-ZlZ-JBRbhaZURjn5Ci3K2g8CXvY1du9uXOXuKgNSPvJYwysmb7bnD7y81SXZ1U37qEy5hZqRRFuiAH2Aponw0-yMqchUCoub-U2G3iuApUWy0wqNvFimB1CTZqCoz3EnQ1rbD6rI2UfmvAMmnZxe65sM8Jn_7a6hHewMGDJsangvA_s5-F1ZwRP3csvLVrSJi7vM_GnGYIWcrL8v1ysuXqF1WtIAII9KK6gD7bfwoaE5eZ_eWe0qaxbKtvXd83TUI-7akTJCC7tj5r2WzPzfZ2nk3GAtbAVyscboreD77WccWKs7nfl8QKNiAH_nxKTHj9bEw4ee8kH8z0HoYXiqqW1eDR-BajESBg_VA0Oqkj8nYD3EIdeVZumSIVePkvcTIoIBGTF0ui-PGOnL7W0YYabZLl6sHiFTy_WlUn2UpgjFgcXtzr5tJBv9Yy-yvSBjyu6evNw_Y7fXmlhb8XZ-k-Z03ChROhyQYZ6fuisAhAfUPfhcBGrxNQeDeNy68hXk0VMql0AuMbSrw_xK6i7JiQbz9vDzu7yGXSvCwpGLYJhvopbm42ZUSaVjhhFu_H5F1iikK5Dzj3Qs17_5MhvcC7UdPe0E6gd4N4niRiarg1xbZ5yH5Pdc8Mqj_BA_c-hh3BxUXiUMLl605ZHl1F7MgXvRLpobSFe9xZSoGKnqfssnB0ntIVe4GjwVgWyoW9BPsnOu3KiEV-ZCMuIfR416xJybcE2cSrmfmNAEtozNRo2DTLtZYf2H0_dQGa105gmjDbJtAni9RIvjB5U9RINbseKG3cyigh1RWVK6ihObGftjtEsBMpLgfDLrnWpdE21GTaWXtXl_1KgbNQ=w929-h852)

[Performance API References Document](https://documenter.getpostman.com/view/21511170/2s7YYu7imm)
