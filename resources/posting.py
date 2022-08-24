from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from mysql_connection import get_connection

# 게시물 작성
class PostingResource(Resource) :
    @jwt_required()
    def post(self) :
        data = request.get_json()
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''insert into posting (userId, title, content)
                        values(%s, %s, %s);'''
            record = (userId, data['title'], data['content'])
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
    
    # 게시물 목록 조회
    def get(self) :
        try :
            connection = get_connection()
            limit = request.args.get('limit')
            offset = request.args.get('offset')
            query = '''
                        select u.nickname, p.*, ifnull(pc.viewCount,0) as viewCount, count(pr.postingId) as recommend
                        from posting p
                        join user u on u.id = p.userId
                        left join postingCount pc on pc.postingId = p.id
                        left join postingRecommend pr on pr.postingId = p.id
                        group by p.id
                        order by createdAt desc
                        limit ''' + limit + ''' offset ''' + offset + ''';
                    '''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
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

# 게시물 수정
class PostingSpecificResource(Resource) :
    @jwt_required()
    def put(self, postingId) :
        data = request.get_json()
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''select userId from posting where id = %s;'''
            record = (postingId, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            posting = resultList[0]

            if posting['userId'] != userId :
                cursor.close()
                connection.close()
                return { "error" : "수정할 수 없습니다."}

            query = '''update posting set title = %s, content = %s where id = %s;'''
            record = (data['title'], data['content'], postingId)
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

    # 게시물 삭제
    @jwt_required()
    def delete(self, postingId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''select userId from posting where id = %s;'''
            record = (postingId, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            posting = resultList[0]

            if posting['userId'] != userId :
                cursor.close()
                connection.close()
                return { "error" : "삭제할 수 없습니다."}

            query = '''delete from posting where id = %s;'''
            record = (postingId, )
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

    # 게시물 상세보기 (댓글 추가 필요 혹은 따로 추가)
    def get(self, postingId) :
        try :
            connection = get_connection()
            query = '''
                        select u.nickname, p.*, ifnull(pc.viewCount,0) as viewCount, count(pr.postingId) as recommend
                        from posting p
                        join user u on u.id = p.userId
                        left join postingCount pc on pc.postingId = p.id
                        left join postingRecommend pr on pr.postingId = p.id
                        where p.id = %s;
                    '''
            record = (postingId, )
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



# 게시물 추천
class PostingRecommendResource(Resource) :
    @jwt_required()
    def post(self, postingId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''insert into postingRecommend (userId, postingId) values (%s, %s);'''
            record = (userId, postingId)
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
    
    # 게시물 추천 취소
    @jwt_required()
    def delete(self, postingId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''delete from postingRecommend where userId = %s and postingId = %s;'''
            record = (userId, postingId)
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


# 내 게시물 조회
class PostingMyPostingResource(Resource) :
    @jwt_required()
    def get(self) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            limit = request.args.get('limit')
            offset = request.args.get('offset')
            query = '''
                        select u.nickname, p.*, ifnull(pc.viewCount,0) as viewCount, count(pr.postingId) as recommend
                        from posting p
                        join user u on u.id = p.userId
                        left join postingCount pc on pc.postingId = p.id
                        left join postingRecommend pr on pr.postingId = p.id
                        group by p.id having p.userId = %s
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

        return { "resultList" : resultList }, 200