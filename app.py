from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from flask_restful import Api
from resources.clovaocr import imgOrcClassifyResource

from resources.party import PartyResource, PartySpecificResource
from resources.perfomance import PerformancePlaceDetailResource, PerformanceSearchResource, PerformancePlaceSearchResource, NearByPerformanceResource, PerformanceLikeResource, PerformanceDetailDBResource, NearPerformanceResource, PerformanceDetailResource
from resources.user import jwt_blacklist, UserRegisterResource, UserLoginResource, UserLogoutResource, UserWithdrawalResource,UserEditPasswordResource, UserEditNicknameResource, UserEditAgeResource, UserEditGenderResource, UserValdationResource, UserInfoResource
from resources.review import ReviewAddResource, ReviewAllListResource, ReviewDeleteResource, ReviewDetailResource, ReviewModifyResource, ReviewMyListResource, ReviewRecommendCancelResource, ReviewRecommendResource, ReviewSearchResource
from resources.posting import PostingRecommenDescResource, PostingResource, PostingSpecificResource, PostingRecommendResource, PostingMyPostingResource
from resources.recommend import PerformaceRecomRealTimeRersource

app = Flask(__name__)

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
# 비밀번호 확인
api.add_resource(UserValdationResource, '/user/validation')
# 회원탈퇴
api.add_resource(UserWithdrawalResource, '/user/withdrawal')
# 회원 비밀번호 수정
api.add_resource(UserEditPasswordResource, '/user/editpassword')
# 회원 닉네임 수정
api.add_resource(UserEditNicknameResource, '/user/editnickname')
# 회원 나이 수정
api.add_resource(UserEditAgeResource, '/user/editage')
# 회원 성별 수정
api.add_resource(UserEditGenderResource, '/user/editgender')
# 회원 정보 확인
api.add_resource(UserInfoResource, '/user')

# 해당 작품 리뷰 보기
api.add_resource(ReviewSearchResource, '/review/<prfId>')
# 내 리뷰 보기
api.add_resource(ReviewMyListResource, '/review/myreview')
# 모든 리뷰 보기
api.add_resource(ReviewAllListResource, '/review')
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
api.add_resource(PerformanceSearchResource, '/performance')
# 공연 상세 조회
api.add_resource(PerformanceDetailResource, '/performancedetail/<prfId>')
# 공연 상세 조회(DB)
api.add_resource(PerformanceDetailDBResource, '/performance/<prfId>')
# 공연 시설 조회
api.add_resource(PerformancePlaceSearchResource, '/performanceplace')
# 공연 시설 상세 조회
api.add_resource(PerformancePlaceDetailResource, '/performanceplace/<plcId>')
# 내 지역(구) 상영중인 공연 검색
api.add_resource(NearByPerformanceResource, '/nearbyperformance/<sidoCodeSub>')
# 반경 내 공연 Map 표시
api.add_resource(NearPerformanceResource, '/nearperformance')
# 공연 좋아요, 좋아요 취소
api.add_resource(PerformanceLikeResource, '/performance/like/<prfId>')

# 포스팅 작성, 목록 조회
api.add_resource(PostingResource, '/posting')
# 포스팅 하나 조회, 수정, 삭제 
api.add_resource(PostingSpecificResource, '/posting/<int:postingId>')
# 포스팅 추천, 추천 취소
api.add_resource(PostingRecommendResource, '/posting/recommend/<int:postingId>')
# 내 포스팅 조회 
api.add_resource(PostingMyPostingResource, '/posting/myposting')
# 게시글 정렬 내림차순 (큰 값부터)
api.add_resource(PostingRecommenDescResource, '/posting/lists')

# 파티생성
api.add_resource(PartyResource, '/party')
# 파티수정, 파티삭제
api.add_resource(PartySpecificResource, '/party/<int:partyId>')
# 실시간 공연 개인화 추천 API
api.add_resource(PerformaceRecomRealTimeRersource, '/performance/recommend')

# 리뷰 작성시 티켓 이미지 인증 확인
api.add_resource(imgOrcClassifyResource, '/imgocr')



if __name__ == '__main__' :
    app.run()