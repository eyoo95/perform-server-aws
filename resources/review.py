from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from mysql_connection import get_connection


# 해당 작품 리뷰 보기
class ReviewSearchResource(Resource) :
    def get(self, prfId) :
        try :
            connection = get_connection()
            limit = request.args.get('limit')
            offset = request.args.get('offset')
            query = '''
                        select p.id, p.mt20id, p.prfnm, u.id as userId, u.nickname, 
                        r.id as reviewId, r.content, r.createdAt, r.updatedAt,
                        count(rr.reviewId) as reviewRecommend
                        from review r
                        join prf p on r.prfId = p.id
                        join user u on r.userId = u.id
                        left join reviewRecommend rr on rr.reviewId = r.id
                        group by r.id having p.id = %s
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

# 내 리뷰 보기
class ReviewMyListResource(Resource) :
    @jwt_required()
    def get(self) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            limit = request.args.get('limit')
            offset = request.args.get('offset')
            query = '''
                        select u.id as userId, u.nickname, 
                        r.id as reviewId, r.title, r.content, r.createdAt, r.updatedAt, count(rr.reviewId)
                        from review r
                        join user u on r.userId = u.id
                        left join reviewRecommend rr on rr.reviewId = r.id
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
            query = '''
                        select p.id, p.mt20id, p.prfnm, u.id as userId, u.nickname, 
                        r.id as reviewId, r.content, r.createdAt, r.updatedAt,
                        count(rr.reviewId) as reviewRecommend
                        from review r
                        join prf p on r.prfId = p.id
                        join user u on r.userId = u.id
                        left join reviewRecommend rr on rr.reviewId = r.id
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
        data = request.get_json()
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''insert into review (userId, prfId, title, content)
                        values(%s, %s, %s, %s);'''
            record = (userId, prfId, data['title'], data['content'])
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

        return { "result" : "success" }, 200

# 리뷰 수정
class ReviewModifyResource(Resource) :
    @jwt_required()
    def put(self, reviewId) :
        data = request.get_json()
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''select userId from review where id = %s;'''
            record = (reviewId, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            review = resultList[0]

            if review['userId'] != userId :
                cursor.close()
                connection.close()
                return { "error" : "수정할 수 없습니다."}

            query = '''update review set title = %s, content = %s where id = %s;'''
            record = (data['title'], data['content'], reviewId)
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

# 리뷰 삭제
class ReviewDeleteResource(Resource) :
    @jwt_required()
    def delete(self, reviewId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''select userId from review where id = %s;'''
            record = (reviewId, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            review = resultList[0]

            if review['userId'] != userId :
                cursor.close()
                connection.close()
                return { "error" : "삭제할 수 없습니다."}

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