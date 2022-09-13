from datetime import datetime
import requests
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from config import Config
from mysql_connection import get_connection
import xmltodict, json
import boto3

userId = 'null'

# 해당 작품 리뷰 보기 (조회)
class ReviewSearchResource(Resource) :
    def get(self, prfId) :
        try :
            connection = get_connection()
            limit = request.args.get('limit')
            offset = request.args.get('offset')
            query = '''
                        select r.id as reviewId, r.prfId, r.prfName, u.id as userId, u.nickName, 
                        r.content, r.createdAt, r.updatedAt, count(rr.reviewId) as reviewRecommend, rc.viewCount, rt.rating
                        from review r
                        join prf on prf.mt20id = r.prfId
                        join prfRating rt on rt.prfId = r.prfId
                        join user u on r.userId = u.id
                        left join reviewRecommend rr on rr.reviewId = r.id
                        left join reviewCount rc on r.id = rc.reviewId
                        group by r.id having r.prfId = %s
                        limit ''' + limit + ''' offset ''' + offset + ''';
                    '''
            record = (prfId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            i = 0
            for record in resultList :
                resultList[i]['createdAt'] = record['createdAt'].isoformat()
                resultList[i]['updatedAt'] = record['updatedAt'].isoformat()
                i += 1
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return { "resultList" : resultList }, 200

# 내 리뷰 보기 (조회)
class ReviewMyListResource(Resource) :
    @jwt_required()
    def get(self) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            limit = request.args.get('limit')
            offset = request.args.get('offset')
            query = '''
                        select u.id as userId, u.nickName, r.id as reviewId, r.prfName,
                        r.title, r.content, r.createdAt, r.updatedAt, count(rr.reviewId) as reviewRecommend, rc.viewCount, rt.rating
                        from review r
                        join prf on prf.mt20id = r.prfId
                        join prfRating rt on rt.prfId = r.prfId
                        join user u on r.userId = u.id
                        left join reviewRecommend rr on rr.reviewId = r.id
                        left join reviewCount rc on r.id = rc.reviewId
                        group by r.id having u.id = %s
                        limit ''' + limit + ''' offset ''' + offset + ''';
                    '''
            record = (userId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            i = 0
            for record in resultList :
                resultList[i]['createdAt'] = record['createdAt'].isoformat()
                resultList[i]['updatedAt'] = record['updatedAt'].isoformat()
                i += 1
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return{ "resultList" : resultList }, 200

# 리뷰 상세 보기
class ReviewDetailResource(Resource) :
    def get(self, reviewId) :
        try :
            connection = get_connection()

            # 리뷰 상세 정보 출력
            query = '''
                        select r.id as reviewId, r.prfId, r.prfName, u.id as userId, u.nickName, 
                        r.content, r.createdAt, r.updatedAt, count(rr.reviewId) as reviewRecommend, rc.viewCount, rt.rating
                        from review r
                        join prf on prf.mt20id = r.prfId
                        join prfRating rt on rt.prfId = r.prfId
                        join user u on r.userId = u.id
                        left join reviewRecommend rr on rr.reviewId = r.id
                        left join reviewCount rc on r.id = rc.reviewId
                        group by r.id having r.id = %s;
                    '''
            record = (reviewId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            i = 0
            for record in resultList :
                resultList[i]['createdAt'] = record['createdAt'].isoformat()
                resultList[i]['updatedAt'] = record['updatedAt'].isoformat()
                i += 1

            # 조회수 증가
            query = '''update reviewCount set viewCount = viewCount+1 where reViewId = %s;'''
            record = (reviewId, )
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return{ "resultList" : resultList }, 200

# 리뷰 작성
class ReviewAddResource(Resource) :
    @jwt_required()
    def post(self, prfId) :

        # 리뷰 작성시 업로드한 이미지 파일과 내용 확인
        file = request.files['photo']
        prfName = request.form['prfName']
        title = request.form['title']
        content = request.form['content']
        rating = request.form['rating']

        # 파일명 변경, 파일명은 유니크 (중복이 없도록)
        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':', '_') + '.png'

        # 클라이언트에서 받은 파일의 이름 변경
        file.filename = new_file_name
        imgUrl = Config.S3_LOCATION+file.filename

        # S3에 업로드, AWS 라이브러리 사용 (boto3)
        s3 = boto3.client('s3', aws_access_key_id = Config.AWS_ACCESS_KEY, \
                    aws_secret_access_key = Config.AWS_SECRET_KEY)
        try :
            s3.upload_fileobj(file, Config.S3_BUCKET, file.filename, \
                ExtraArgs={'ACL':'public-read', 'ContentType':file.content_type})
        except Exception as e :
            return {'error' : str(e)}, 500


        # 리뷰 작성과 조회수 초기화
        try :
            connection = get_connection()
            userId = get_jwt_identity()

            # 리뷰 작성
            query = '''insert into review (userId, prfId, prfName, title, content, imgUrl)
                        values(%s, %s, %s, %s, %s, %s);'''
            record = (userId, prfId, prfName, title, content, imgUrl)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()


            # 별점 추가 
            query = '''insert into prfRating
                        (userId, prfId, rating)
                        values
                        (%s, %s, %s);'''
            record = (userId, prfId, rating)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            # 작성한 리뷰 조회수 초기화를 위한 리뷰 ID 확인
            query = ''' select id from review where userId = %s order by id desc limit 1;'''
            record = (userId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()

            # 해당 리뷰 조회수 생성
            query = '''insert into reviewCount (reviewId, userId) values (%s, %s);'''
            record = (resultList[0]['id'], userId)
            print(resultList[0]['id'])
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            #cursor.close()
            connection.close()


            # 관람 인증 확인 기능
            # 글자 인식 인공지능 API 설정 (Clova OCR)
            request_json = {
                'images': [
                    {
                        'format': 'png',
                        'name': 'test1',
                        'url' : imgUrl
                    }
                ],
                'lang' : 'ko',
                'requestId': str(uuid.uuid4()),
                'version': 'V2',
                'timestamp': int(round(time.time() * 1000))
            }

            payload = json.dumps(request_json).encode('UTF-8')
            headers = {
                'X-OCR-SECRET': Config.CLOVA_ACCESS_KEY,
                'Content-Type': 'application/json'
            }

            # 글자 인식 인공지능 API 호출 (Clova OCR)
            response = requests.request("POST", Config.CLOVA_BASE_URL, headers=headers, data = payload)
            response = response.json()
            print(response)

            # 공연 이름 특수 문자 제거
            textTranslator = prfName.maketrans({
                "." : "", "," : "", "[" : "", "]" : "",
                "(" : "", ")" : "", "!" : "", "~" : "",
                "-" : "", ":" : "", "|" : "", "@" : "",
                "@" : "", "#" : "", "$" : "", "%" : "",
                "^" : "", "&" : "", "*" : "", "/" : "",
                "+" : "", "-" : "`", "_" : "", "=" : "",
                "'" : "", "\"" : "", "<" : "", ">" : "", "\\" : ""
                })
            prfName = prfName.translate(textTranslator).upper()

            # 공연 이름 단어별 분리
            prfNameList = []
            prfNameList.append(prfName.split())

            print("prfName List : ", prfNameList)

            # 글자 인식 정보 저장
            fields = response['images'][0]['fields']

            # 인식된 글자 특수 문자 제거
            inferTextList = []
            for i in range( len(fields) ) :
                inferTextList.append( fields[i]['inferText'].upper() )
            inferText= " ".join(inferTextList).translate(textTranslator)
            inferTextList = []
            inferTextList.append(inferText.split())

            print("inferText List : ", inferTextList)

            # 공연 이름과 티켓의 글자가 일치하는지 검사
            classifyCount = 0
            for i in range ( len(prfNameList[0]) ) :
                for j in range ( len(inferTextList[0]) ) :
                    if prfNameList[0][i] in inferTextList[0][j] :
                        classifyCount += 1
                        print(prfNameList[0][i], inferTextList[0][j])
                        break
                        

            print("name split number : ", len(prfNameList[0]))
            print("classify count : ", classifyCount)

            # 공연 이름과 얼마나 일치하는지 정확도 표시
            imgAcc = ( classifyCount / len(prfNameList[0]) ) * 100
            print("imgAcc : ", imgAcc,"%")

            # 공연 이름과 티켓 이름의 표기가 다를 수 있으므로 적당한 승인 퍼센테이지 조정
            if imgAcc >= 85 :
                certify = 1 # 티켓 인증
            else :
                certify = 0 # 티켓 인증 불합격

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return { "result" : certify, #certify,
                "accurate" : imgAcc,
                "imgUrl" : imgUrl }, 200

# 리뷰 삭제
class ReviewDeleteResource(Resource) :
    @jwt_required()
    def delete(self, reviewId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()

            # prfID 확인
            query = '''select prfId from review where id = %s;'''
            record = (reviewId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            prfId = resultList[0]['prfId']
            cursor.close()
            

            # 해당 리뷰의 별점 삭제
            query = '''delete from prfRating where userId = {} and prfId = "{}" ;'''.format(userId, prfId)
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            cursor.close()

            # 리뷰 삭제
            query = '''delete from review where id = %s;'''
            record = (reviewId, )
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return {"result" : "success"}, 200

# 리뷰 추천
class ReviewRecommendResource(Resource) :
    @jwt_required()
    def post(self, reviewId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''insert into reviewRecommend (userId, reviewId) values (%s, %s);'''
            record = (userId, reviewId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return{ "result" : "success" }, 200
    
# 리뷰 추천 취소
class ReviewRecommendCancelResource(Resource) :
    @jwt_required()
    def delete(self, reviewId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''delete from reviewRecommend where userId = %s and reviewId = %s;'''
            record = (userId, reviewId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return{ "result" : "success" }, 200