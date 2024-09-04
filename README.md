# 공연 조회 API 서버 (뭐보러갈래) Overview
- 공연 정보와 내 지역의 공연 정보를 확인 할 수 있습니다.
- 사용자 기반 협업 필터링을 활용한 추천 인공지능으로 사용자들의 활동 패턴을 확인하고 좋아 할 것 같은 공연을 추천하는 기능을 포함하고 있습니다.
- 공연 티켓 이미지를 업로드하면 이미지의 글자를 판독하여 해당 공연과 일치하는 공연 티켓인지 확인하는 인공지능 기능을 포함하고 있습니다.
- 보안을 위해 환경 설정 파일 'config.py', 'mysql_connection.py' 의 일부 변수 조정으로 인해 정상적인 실행이 되지 않음을 알려드립니다.

# GitHub
[PerformanceSearchAPI GitHub](http://)

# Repository File Structure

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

[Performance API References Document](https://documenter.getpostman.com/view/21511170/2s7YYu7imm)
