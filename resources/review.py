import requests
from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from config import Config
from mysql_connection import get_connection
import boto3
import time
import uuid
import json

userId = 'null'

# 해당 작품 리뷰 보기 (조회)
class ReviewSearchResource(Resource) :
    def get(self, prfId) :
        try :
            connection = get_connection()
            limit = request.args.get('limit')
            offset = request.args.get('offset')
            query = '''
                        select r.id as reviewId, r.prfId, r.prfName, u.id as userId, u.nickName, r.verified,
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
                        select u.id as userId, u.nickName, r.id as reviewId, r.prfName, r.verified,
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
                        select r.id as reviewId, r.prfId, r.prfName, u.id as userId, u.nickName, r.verified,
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

        # 리뷰 작성시 내용 확인
        data = request.get_json()
        prfName = data['prfName']
        title = data['title']
        content = data['content']
        rating = data['rating']
        imgUrl = data['imgUrl']
        verified = data['verified']

        # 리뷰 작성과 조회수 초기화
        try :
            connection = get_connection()
            userId = get_jwt_identity()

            # 리뷰 작성
            query = '''insert into review (userId, prfId, prfName, title, content, imgUrl, verified)
                        values(%s, %s, %s, %s, %s, %s, %s);'''
            record = (userId, prfId, prfName, title, content, imgUrl, verified)
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

            # prfID 확인
            query = '''select prfId from review where id = %s;'''
            record = (reviewId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            prfId = resultList[0]['prfId']

            # 수정
            query = '''update review set title = %s, content = %s where id = %s;'''
            record = (data['title'], data['content'], reviewId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            
            # 별점 수정 
            query = '''update prfRating set rating = %s where prfId = %s and userId = %s;'''
            record = (data['rating'], prfId, userId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return {"result" : "success"}, 200

# 리뷰 삭제
class ReviewDeleteResource(Resource) :
    def delete(self, reviewId) :
        try :
            connection = get_connection()
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