from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from flask_restful import Resource
from mysql_connection import get_connection
import mysql.connector
from email_validator import validate_email, EmailNotValidError
from utils import hash_password, check_password
import datetime


class UserRegisterResource(Resource):
    # 회원가입하는 API
    def post(self):
        data = request.get_json()

        # 이메일 주소형식을 확인한다.

        try:            
            validate_email(data['email'])

        except EmailNotValidError as e:
            print(str(e))
            return {'error' : str(e), 'error_no':1} , 400

        # 비밀번호 암호화
        # 비밀번호의 길이가 유효한지 체크한다. 4자리이상 12자리이상
        if len(data['password']) < 4 or len(data['password'])>12:
            return{'error': '비밀번호 길이는 4자리 이상 12자리 이하이어야 합니다.', 'error_no':2}, 400

        hashed_password = hash_password(data['password'])

        # 데이터베이스에 회원정보를 저장한다.

        try :

            # 데이터 insert 
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''insert into user
                    (nickname, email, password, age, gender)
                    values
                    (%s, %s, %s, %s, %s);'''

            record = (data['nickname'], data['email'], hashed_password, data['age'], data['gender'] ) # 튜플형식
            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record )

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # DB에 저장된 ID값 가져오기
            user_id = cursor.lastrowid

            # 6. 자원 해제
            cursor.close()

            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e), 'error_no':3}, 503 
        
        # user_id를 바로 보내면 안되고 JWT로 암호화한뒤 보낸다.
        access_token = create_access_token(user_id)

        return {"result":"success" , "accessToken" : access_token}, 200

class UserLoginResource(Resource):

    # 로그인하는 API
    def post(self):
        # 클라이언트로부터 body로 넘어온 데이터를 받는다.
        data = request.get_json()

        # {
        #     "email": "abc@naver.com",
        #     "password": "123456"
        # }
        try:
            connection = get_connection()
            # 이메일로 DB의 데이터를 가져온다.
            query = '''select * from user
                        where email = %s;'''

            record = (data['email'],  )

            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query, record )

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()
            
            # 중요! DB 에서 가져온 timestamp는 파이썬의 datetime으로 자동 변경된다.
            # 문제는 이 데이터를 json.으로 바로 보낼수 없으므로 문자열로 바꿔서 다시 저장해서 보낸다.

            i = 0
            for record in result_list:
                result_list[i]['createdAt'] = record['createdAt'].isoformat()
                result_list[i]['updatedAt'] = record['updatedAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, 503

        # result_list의 행의갯수가 1개면 유저데이터를 받아온것이고 0 이면 등록되지 않은 회원
        if len(result_list) != 1:
            return {'error':'해당되는 이메일 정보가 없습니다.', 'error_no':6}, 400

        # 비밀번호가 맞는지 확인
        user_info = result_list[0]
        check = check_password(data['password'],user_info['password'])
        if check == False:
            return {'error':'비밀번호가 맞지 않습니다.', 'error_no':7}, 400

        access_token = create_access_token(user_info['id'])
        
        return {'result' : 'success' ,'accessToken':access_token} ,200

jwt_blacklist = set()
# 로그아웃하는 기능의 클래스
class UserLogoutResource(Resource):

    @jwt_required()
    def post(self):

        jti = get_jwt()['jti']
        print(jti)

        jwt_blacklist.add(jti)
        return {'result':'success'}, 200

# 회원탈퇴하는 클래스
class UserWithdrawalResource(Resource):

    @jwt_required()
    def delete(self):
        
        try : 
            # 1. DB에 연결
            connection = get_connection()
            userId = get_jwt_identity()          

            # 2. 쿼리문 만들기
            query = '''delete from user
                        where Id = %s;'''

            record = (userId,) # 튜플형식


            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다.
            cursor.execute(query, record )

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error':str(e)}, 503

        return {'result': 'success'} , 200

# 회원 비밀번호 수정하는 클래스
class UserEditPasswordResource(Resource):

    @jwt_required()
    def put(self) :

        # body에서 전달된 데이터를 처리
        data = request.get_json()
        userId = get_jwt_identity()

        # 비밀번호 암호화
        # 비밀번호의 길이가 유효한지 체크한다. 4자리이상 12자리이상
        if len(data['password']) < 4 or len(data['password'])>12:
            return{'error': '비밀번호 길이는 4자리 이상 12자리 이하이어야 합니다.', 'error_no':2}, 400

        hashed_password = hash_password(data['password'])

        # 디비 업데이트 실행코드
        try :
            # 데이터 업데이트 
            # 1. DB에 연결
            connection = get_connection()

            query = '''update user
                        set password = %s
                        where id = %s;'''

            record = (hashed_password, userId)
           
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 503

        return {'result' :'success'}, 200


# 회원 닉네임 수정하는 클래스
class UserEditNicknameResource(Resource):

    @jwt_required()
    def put(self) :

        # body에서 전달된 데이터를 처리
        data = request.get_json()
        userId = get_jwt_identity()

        # 디비 업데이트 실행코드
        try :
            # 데이터 업데이트 
            # 1. DB에 연결
            connection = get_connection()

            query = '''update user
                        set nickname = %s
                        where id = %s;'''

            record = (data['nickname'], userId)
           
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 503

        return {'result' :'success'}, 200        


# 회원 나이 수정하는 클래스
class UserEditAgeResource(Resource):

    @jwt_required()
    def put(self) :

        # body에서 전달된 데이터를 처리
        data = request.get_json()
        userId = get_jwt_identity()

        # 디비 업데이트 실행코드
        try :
            # 데이터 업데이트 
            # 1. DB에 연결
            connection = get_connection()

            query = '''update user
                        set age = %s
                        where id = %s;'''

            record = (data['age'], userId)
           
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 503

        return {'result' :'success'}, 200

# 회원 성별 수정하는 클래스
class UserEditGenderResource(Resource):

    @jwt_required()
    def put(self) :

        # body에서 전달된 데이터를 처리
        data = request.get_json()
        userId = get_jwt_identity()

        # 디비 업데이트 실행코드
        try :
            # 데이터 업데이트 
            # 1. DB에 연결
            connection = get_connection()

            query = '''update user
                        set gender = %s
                        where id = %s;'''

            record = (data['gender'], userId)
           
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다 => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 503

        return {'result' :'success'}, 200

class UserValdationResource(Resource):

    # 비밀번호 확인하는 API
    @jwt_required()
    def post(self):
        # 클라이언트로부터 body로 넘어온 데이터를 받는다.
        data = request.get_json()
        userId = get_jwt_identity()

        try:
            connection = get_connection()
            # 이메일로 DB의 데이터를 가져온다.
            query = '''select * from user
                        where id = %s;'''

            record = (userId,  )

            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query, record )

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            result_list = cursor.fetchall()
            
            # 중요! DB 에서 가져온 timestamp는 파이썬의 datetime으로 자동 변경된다.
            # 문제는 이 데이터를 json.으로 바로 보낼수 없으므로 문자열로 바꿔서 다시 저장해서 보낸다.

            i = 0
            for record in result_list:
                result_list[i]['createdAt'] = record['createdAt'].isoformat()
                result_list[i]['updatedAt'] = record['updatedAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e)}, 503

        # 비밀번호가 맞는지 확인
        user_info = result_list[0]
        check = check_password(data['password'],user_info['password'])
        if check == False:
            return {'error':'비밀번호가 일치하지 않습니다.', 'error_no':7}, 400
        
        return {'result' : 'success'} ,200

# 회원정보 받는 클래스
class UserInfoResource(Resource):
    @jwt_required()
    def get(self) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()

            query = '''
                        select id, nickname, email, age, gender
                        from user
                        where id = %s;
                    '''

            record = ( userId,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()
            userInfo = resultList[0]
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE

        return { "userInfo" : userInfo }, 200