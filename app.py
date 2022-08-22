from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from flask_restful import Api
from resources.perfomance import PerformanceDetailResource, PerformancePlaceDetailResource, PerformanceSearchResource, PerformancePlaceSearchResource
from resources.user import jwt_blacklist, UserRegisterResource, UserLoginResource, UserLogoutResource, UserWithdrawalResource,UsereditResource
from resources.review import ReviewAddResource, ReviewDeleteResource, ReviewDetailResource, ReviewModifyResource, ReviewMyListResource, ReviewRecommendCancelResource, ReviewRecommendResource, ReviewSearchResource
from resources.posting import PostingResource, PostingSpecificResource, PostingRecommendResource, PostingMyPostingResource

app = Flask(__name__)
# 브렌치 테스트

# 환경변수 세팅
app.config.from_object(Config)

# JWT 토큰 라이브러리 만들기
jwt = JWTManager(app)

# 로그아웃된 토큰이 들어있는 set을 jwt에 알려준다
@jwt.token_in_blocklist_loader
def check_if_token_is_revoke(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

# 경로와 resource(API 코드)를 연결한다.

# 회원가입
api.add_resource(UserRegisterResource, '/user/register')
# 로그인
api.add_resource(UserLoginResource, '/user/login')
# 로그아웃
api.add_resource(UserLogoutResource, '/user/logout')
# 회원탈퇴
api.add_resource(UserWithdrawalResource, '/user/withdrawal')
# 회원정보 수정
api.add_resource(UsereditResource, '/user/editinfo')

# 해당 작품 리뷰 보기
api.add_resource(ReviewSearchResource, '/review/<prfId>')
# 내 리뷰 보기
api.add_resource(ReviewMyListResource, '/review/myreview')
# 리뷰 상세 보기
api.add_resource(ReviewDetailResource, '/review/detail/<int:reviewId>')
# 리뷰 작성
api.add_resource(ReviewAddResource, '/review/<prfId>')
# 리뷰 수정
api.add_resource(ReviewModifyResource, '/review/<int:reviewId>')
# 리뷰 삭제
api.add_resource(ReviewDeleteResource, '/review/<int:reviewId>')
# 리뷰 추천
api.add_resource(ReviewRecommendResource, '/review/recommend/<int:reviewId>')
# 리뷰 추천 취소
api.add_resource(ReviewRecommendCancelResource, '/review/recommend/<int:reviewId>')

# 공연 조회
api.add_resource(PerformanceSearchResource, '/performancesearch')
# 공연 상세 조회
api.add_resource(PerformanceDetailResource, '/performancedetail/<prfId>')
# 공연 시설 조회
api.add_resource(PerformancePlaceSearchResource, '/performanceplacesearch')
# 공연 시설 상세 조회
api.add_resource(PerformancePlaceDetailResource, '/performanceplacedetail/<plcId>')

# 포스팅 작성, 목록 조회
api.add_resource(PostingResource, '/posting')
# 포스팅 하나 조회, 수정, 삭제 
api.add_resource(PostingSpecificResource, '/posting/<int:postingId>')
# 포스팅 추천, 추천 취소
api.add_resource(PostingRecommendResource, '/posting/recommend/<int:postingId>')
# 내 포스팅 조회 
api.add_resource(PostingMyPostingResource, '/posting/myposting')


if __name__ == '__main__' :
    app.run()