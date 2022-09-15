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

# 리뷰 작성
class imgOrcClassifyResource(Resource) :
    def post(self) :

        # 리뷰 작성시 업로드한 이미지 파일과 내용 확인
        file = request.files['photo']
        prfName = request.form['prfName']

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
            verified = 1 # 티켓 인증
        else :
            verified = 0 # 티켓 인증 불합격

        return {
            "verified" : verified,
            "imgUrl" : imgUrl,
            "accurate" : imgAcc
                }, 200