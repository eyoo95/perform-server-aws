from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector
from mysql_connection import get_connection

class PartyResource(Resource) :

    # 파티생성
    @jwt_required()
    def post(self) :
        data = request.get_json()
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''insert into partyRoom (userId, prfnm, title)
                        values(%s, %s, %s);'''
            record = (userId, data['prfnm'] ,data['title'])
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            partyId = cursor.lastrowid
            print(partyId)

            cursor.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        try :
            query = '''insert into partyCrew (userId, partyId)
                        values(%s, %s);'''
            record = (userId, partyId)
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
    
    # 파티 목록 조회
    def get(self) :

        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리한다.  
        
        limit = request.args['limit']
        offset = request.args['offset']
        keyword = request.args['keyword']
        searchType = request.args['searchType']

        # 공연 여부
        if searchType == "title":
            searchType = "title like '%"+keyword+"%'"
        elif searchType == "prfnm":
            searchType = "prfnm like '%"+keyword+"%'"
        elif searchType == "all":
            searchType ="title like '%"+keyword+"%' or prfnm like '%"+keyword+"%'"

        try :
            connection = get_connection()
            
            query = '''
                        select pt.*, u.nickname
                        from partyRoom as pt
                        left join user as u on pt.userId = u.id
                        where '''+searchType+'''
                        limit ''' + limit + ''' offset ''' + offset + ''';
                    '''

            print(query)

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

class PartySpecificResource(Resource) :
    # 파티 수정
    @jwt_required()
    def put(self, partyId) :
        data = request.get_json()
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''select userId from partyRoom where id = %s;'''
            record = (partyId, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            party = resultList[0]

            if party['userId'] != userId :
                cursor.close()
                connection.close()
                return { "error" : "수정할 수 없습니다."}

            query = '''
                        update partyRoom
                        set prfnm = %s, title = %s
                        where id = %s;
                    '''
            record = (data['prfnm'], data['title'], partyId)
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
    def delete(self, partyId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''select userId from partyRoom where id = %s;'''
            record = (partyId, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            party = resultList[0]

            if party['userId'] != userId :
                cursor.close()
                connection.close()
                return { "error" : "삭제할 수 없습니다."}

            query = '''delete from partyCrew where partyId = %s'''
            record = (partyId,)
            cursor = connection.cursor()
            cursor.execute(query, record)

            query = '''delete from partyRoom where id = %s;'''
            record = (partyId, )
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