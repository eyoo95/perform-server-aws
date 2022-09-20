import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host = 'yourhost',  # sql 호스트네임 작성
        database = 'yourdatabase',
        user = 'youruser',  # SQL 에서 작성한 레시피 앱 사용자 계정
        password = 'yourpassword'
    )
    return connection