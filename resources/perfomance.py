# OpenAPI 이용하려면 requests 라이브러리 이용
from unittest import result
import requests

from flask import request
from flask_restful import Resource
import xmltodict
import json
from config import Config

import mysql.connector
from mysql_connection import get_connection

# 공연 조회
class PerformanceSearchResource(Resource):
    def get(self) :
        # 파라미터로 검색 조건 받기
        # 필수 파라미터
        stdate = request.args['stdate'] # 공연시작일자, 6자로 입력받기 ex) 20220701
        eddate = request.args['eddate'] # 공연종료일자, 6자로 입력받기 ex) 20220801
        cpage = request.args['cpage'] # 현재 페이지, 정수형으로 입력
        rows = request.args['rows'] # 페이지당 목록 수, 정수형으로 입력

        # 선택 파라미터
        shprfnm = request.args['shprfnm'] # 공연명
        shprfnmfct = request.args['shprfnmfct'] # 공연시설명
        shcate = request.args['shcate'] # 장르 코드
        signgucode = request.args['signgucode'] # 지역(시도) 코드
        prfstate = request.args['prfstate'] # 공연 상태 코드

        params = {
            "service" : Config.KOPIS_ACCESS_KEY,
            "stdate" : stdate,
            "eddate" : eddate,
            "cpage" : cpage,
            "rows" : rows,
            "shprfnm" : shprfnm,
            "shprfnmfct" : shprfnmfct,
            "shcate" : shcate,
            "signgucode" : signgucode,
            "prfstate" : prfstate
        }
        # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
        response = requests.get(Config.KOPIS_PERFORMANCE_SERARCH_URL, params=params)

        # json 형태로 변환
        xmlToJsonConverter = xmltodict.parse(response.text)

        # json 타입으로 변경
        resultList = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']

        if len(resultList) == 9:
            extra_list = []
            extra_list.append(resultList)
            resultList = extra_list


        return { "resultList" : resultList }, 200

# 공연 상세 조회
class PerformanceDetailResource(Resource):

    def get(self, prfId) :
        # 파라미터에 들어갈 정보
        params = { "service" : Config.KOPIS_ACCESS_KEY }

        # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
        response = requests.get(Config.KOPIS_PERFORMANCE_DETAIL_URL + prfId, params = params)

        # json 형태로 변환
        xmlToJsonConverter = xmltodict.parse(response.text)

        # json 타입으로 변경
        resultList = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']


        return { "resultList" : resultList }, 200

    # DB에 상세 정보 저장
    def post(self, prfId) :
        # 파라미터에 들어갈 정보
        params = { "service" : Config.KOPIS_ACCESS_KEY }

        # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
        response = requests.get(Config.KOPIS_PERFORMANCE_DETAIL_URL + prfId, params = params)

        # json 형태로 변환
        xmlToJsonConverter = xmltodict.parse(response.text)

        # json 타입으로 변경
        resultList = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']

        mt20id = resultList['mt20id']
        prfnm = resultList['prfnm']
        prfpdfrom = resultList['prfpdfrom']
        prfpdto = resultList['prfpdto']
        fcltynm = resultList['fcltynm']
        prfcast = resultList['prfcast']
        prfcrew = resultList['prfcrew']
        prfruntime = resultList['prfruntime']
        prfage = resultList['prfage']
        entrpsnm = resultList['entrpsnm']
        pcseguidance = resultList['pcseguidance']
        poster = resultList['poster']
        sty = resultList['sty']
        genrenm = resultList['genrenm']
        prfstate = resultList['prfstate']
        openrun = resultList['openrun']
        mt10id = resultList['mt10id']
        dtguidance = resultList['dtguidance']

        connection = get_connection()

        try :
            query = '''insert into prf
                        (mt20id , prfnm , prfpdfrom , prfpdto , fcltynm , prfcast , prfcrew , prfruntime , prfage , entrpsnm , pcseguidance , poster , sty , genrenm , prfstate , openrun , mt10id , dtguidance)
                        values
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
            record = (mt20id , prfnm , prfpdfrom , prfpdto , fcltynm , prfcast , prfcrew , prfruntime , prfage , entrpsnm , pcseguidance , poster , sty , genrenm , prfstate , openrun , mt10id , dtguidance)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()

        return { "result" : "success" }, 200

# 공연 시설 조회
class PerformancePlaceSearchResource(Resource):
    def get(self) :
        # 파라미터로 검색 조건 받기
        # 필수 파라미터
        cpage = request.args['cpage'] # 현재 페이지, 정수형으로 입력
        rows = request.args['rows'] # 페이지당 목록 수, 정수형으로 입력

        # 선택 파라미터
        shprfnmfct = request.args['shprfnmfct'] # 공연시설명
        signgucode = request.args['signgucode'] # 시도 코드

        # 파라미터에 들어갈 정보
        params = {
            "service" : Config.KOPIS_ACCESS_KEY,
            "cpage" : cpage,
            "rows" : rows,
            "shprfnmfct" : shprfnmfct,
            "signgucode" : signgucode
        }

        # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
        response = requests.get(Config.KOPIS_PERFORMANCE_PLACE_SERACH_URL, params=params)

        # json 형태로 변환
        xmlToJsonConverter = xmltodict.parse(response.text)

        # json 타입으로 변경
        resultList = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']

        if len(resultList) == 7:
            extra_list = []
            extra_list.append(resultList)
            resultList = extra_list

        return { "resultList" : resultList }, 200

# 공연 시설 상세 조회
class PerformancePlaceDetailResource(Resource):
    def get(self, plcId) :
        # 파라미터에 들어갈 정보
        params = {
            "service" : Config.KOPIS_ACCESS_KEY,
        }
        print(params)
        # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
        response = requests.get(Config.KOPIS_PERFORMANCE_PLACE_DETAIL_URL + plcId, params = params)

        # json 형태로 변환
        xmlToJsonConverter = xmltodict.parse(response.text)

        # json 타입으로 변경
        resultList = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']

        extra_list = []
        extra_list.append(resultList)
        resultList = extra_list

        return { "resultList" : resultList }, 200