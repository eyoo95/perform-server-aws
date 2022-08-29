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

    # # DB에 전체 공연 정보 저장
    # def post(self) :

    #     # 파라미터로 검색 조건 받기
    #     # 필수 파라미터
    #     stdate = request.args['stdate'] # 공연시작일자, 6자로 입력받기 ex) 20220701
    #     eddate = request.args['eddate'] # 공연종료일자, 6자로 입력받기 ex) 20220801
    #     cpage = request.args['cpage'] # 현재 페이지, 정수형으로 입력
    #     rows = request.args['rows'] # 페이지당 목록 수, 정수형으로 입력

    #     # 선택 파라미터
    #     shprfnm = request.args['shprfnm'] # 공연명
    #     shprfnmfct = request.args['shprfnmfct'] # 공연시설명
    #     shcate = request.args['shcate'] # 장르 코드
    #     signgucode = request.args['signgucode'] # 지역(시도) 코드
    #     prfstate = request.args['prfstate'] # 공연 상태 코드

    #     params = {
    #         "service" : Config.KOPIS_ACCESS_KEY,
    #         "stdate" : stdate,
    #         "eddate" : eddate,
    #         "cpage" : cpage,
    #         "rows" : rows,
    #         "shprfnm" : shprfnm,
    #         "shprfnmfct" : shprfnmfct,
    #         "shcate" : shcate,
    #         "signgucode" : signgucode,
    #         "prfstate" : prfstate
    #     }
    #     # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
    #     response = requests.get(Config.KOPIS_PERFORMANCE_SERARCH_URL, params=params)

    #     # json 형태로 변환
    #     xmlToJsonConverter = xmltodict.parse(response.text)

    #     # json 타입으로 변경
    #     resultList = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']



    #     # 파라미터에 들어갈 정보
    #     params = { "service" : Config.KOPIS_ACCESS_KEY }

    #     # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
    #     response = requests.get(Config.KOPIS_PERFORMANCE_DETAIL_URL + prfId, params = params)

    #     # json 형태로 변환
    #     xmlToJsonConverter = xmltodict.parse(response.text)

    #     # json 타입으로 변경
    #     resultList = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']

    #     mt20id = resultList['mt20id']
    #     prfnm = resultList['prfnm']
    #     prfpdfrom = resultList['prfpdfrom']
    #     prfpdto = resultList['prfpdto']
    #     fcltynm = resultList['fcltynm']
    #     prfcast = resultList['prfcast']
    #     prfcrew = resultList['prfcrew']
    #     prfruntime = resultList['prfruntime']
    #     prfage = resultList['prfage']
    #     entrpsnm = resultList['entrpsnm']
    #     pcseguidance = resultList['pcseguidance']
    #     poster = resultList['poster']
    #     sty = resultList['sty']
    #     genrenm = resultList['genrenm']
    #     prfstate = resultList['prfstate']
    #     openrun = resultList['openrun']
    #     mt10id = resultList['mt10id']
    #     dtguidance = resultList['dtguidance']

    #     connection = get_connection()

    #     try :
    #         query = '''insert into prf
    #                     (mt20id , prfnm , prfpdfrom , prfpdto , fcltynm , prfcast , prfcrew , prfruntime , prfage , entrpsnm , pcseguidance , poster , sty , genrenm , prfstate , openrun , mt10id , dtguidance)
    #                     values
    #                     (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
    #         record = (mt20id , prfnm , prfpdfrom , prfpdto , fcltynm , prfcast , prfcrew , prfruntime , prfage , entrpsnm , pcseguidance , poster , sty , genrenm , prfstate , openrun , mt10id , dtguidance)
    #         cursor = connection.cursor()
    #         cursor.execute(query, record)
    #         connection.commit()
    #         cursor.close()
    #         connection.close()

    #     except mysql.connector.Error as e :
    #         print(e)
    #         cursor.close()
    #         connection.close()

    #     return { "result" : "success" }, 200

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

    # 상세정보 볼 때 DB에 공연 정보 저장
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


        return { "resultList" : resultList }, 200

    # DB에 공연장 정보 저장
    def post(self) :
        # 파라미터로 검색 조건 받기
        # 필수 파라미터
        cpage = request.args['cpage'] # 현재 페이지, 정수형으로 입력

        # 선택 파라미터
        shprfnmfct = request.args['shprfnmfct'] # 공연시설명
        signgucode = request.args['signgucode'] # 시도 코드

        # 파라미터에 들어갈 정보
        params = {
            "service" : Config.KOPIS_ACCESS_KEY,
            "cpage" : cpage,
            "rows" : 100000,
            "shprfnmfct" : shprfnmfct,
            "signgucode" : signgucode
        }

        # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
        response = requests.get(Config.KOPIS_PERFORMANCE_PLACE_SERACH_URL, params=params)

        # json 형태로 변환
        xmlToJsonConverter = xmltodict.parse(response.text)

        # json 타입으로 변경
        resultList = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']

        # 파라미터에 들어갈 정보 변경
        params = {
            "service" : Config.KOPIS_ACCESS_KEY,
        }

        plcIdList = []
        for i in range(len(resultList)):
            plcIdList.append(resultList[i]['mt10id'])

        for i in plcIdList:

            # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
            response = requests.get(Config.KOPIS_PERFORMANCE_PLACE_DETAIL_URL + i, params = params)

            # json 형태로 변환
            xmlToJsonConverter = xmltodict.parse(response.text)

            # json 타입으로 변경
            resultList = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']


            fcltynm = resultList['fcltynm']
            mt10id = resultList['mt10id']
            mt13cnt = resultList['mt13cnt']
            fcltychartr = resultList['fcltychartr']
            opende = resultList['opende']
            seatscale = resultList['seatscale']
            telno = resultList['telno']
            relateurl = resultList['relateurl']
            adres = resultList['adres']
            la = resultList['la']  # double
            lo = resultList['lo']  # double


            connection = get_connection()

            try :
                query = '''insert into prfPlace
                            (fcltynm , mt10id , mt13cnt , fcltychartr, opende , seatscale , telno , relateurl , adres , la , lo)
                            values
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
                record = (fcltynm , mt10id , mt13cnt , fcltychartr , opende , seatscale , telno , relateurl , adres , la , lo)
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



# 내 주변 공연 조회
class NearByPerformanceResource(Resource) :
    def get(self, sidoCode, lat, lng) :
        # 내 지역 공연 조회
        # 필수 파라미터
        stdate = request.args['stdate'] # 공연시작일자, 6자로 입력받기 ex) 20220701
        eddate = request.args['eddate'] # 공연종료일자, 6자로 입력받기 ex) 20220801
        cpage = request.args['cpage'] # 현재 페이지, 정수형으로 입력
        rows = request.args['rows'] # 페이지당 목록 수, 정수형으로 입력
        prfstate = request.args['prfstate'] # 공연 상태 코드
        signgucode = sidoCode # 지역(시도) 코드
        latitude = lat # 내 위치 위도
        longitude = lng # 내 위치 경도

        params = {  "service" : Config.KOPIS_ACCESS_KEY,
                    "stdate" : stdate,
                    "eddate" : eddate,
                    "cpage" : cpage,
                    "rows" : rows,
                    "signgucode" : signgucode,
                    "prfstate" : prfstate }
        # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
        response = requests.get(Config.KOPIS_PERFORMANCE_SERARCH_URL, params=params)
        # json 형태로 변환
        xmlToJsonConverter = xmltodict.parse(response.text)
        # json 타입으로 변경
        res = json.loads(json.dumps(xmlToJsonConverter))
        if res['dbs'] is None :
            return {"resultList" : "현재 진행중인 공연이 없습니다."}
        resultList = res['dbs']['db']
        

        if len(resultList) == 9:
            extra_list = []
            extra_list.append(resultList)
            resultList = extra_list


        # 공연 상세 조회
        # 공연과 시설의 정보 저장
        try : 
            performanceList = []
            for i in range(len(resultList)) :
            # 파라미터에 들어갈 정보
                params = { "service" : Config.KOPIS_ACCESS_KEY }
                # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
                response = requests.get(Config.KOPIS_PERFORMANCE_DETAIL_URL + resultList[i]['mt20id'], params = params)
                # json 형태로 변환
                xmlToJsonConverter = xmltodict.parse(response.text)
                # json 타입으로 변경
                res = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']
                performanceList.append([ res['mt20id'], res['prfnm'], res['mt10id'], res['fcltynm'] ])
        except Exception as e :
            print(e)
        #print("placeList : ", performanceList)


        # 공연 시설 상세 조회
        # 공연 시설의 경도 위도를 저장
        performanceDetailList = []
        try :
            for i in range(len(performanceList)) :
                # 파라미터에 들어갈 정보
                params = { "service" : Config.KOPIS_ACCESS_KEY }
                # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
                response = requests.get(Config.KOPIS_PERFORMANCE_PLACE_DETAIL_URL + performanceList[i][2], params = params)
                # json 형태로 변환
                xmlToJsonConverter = xmltodict.parse(response.text)
                # json 타입으로 변경
                res = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']
                performanceDetailList.append([ performanceList[i], res['la'], res['lo'] ])
        except Exception as e :
            print(e)
        #print("performanceDetailList : ", performanceDetailList)


        # 구글맵 API 주위 건물 검색
        # 내 주위 5km에 상영중인 시설 위치 찾기
        nearByPlaceList = []
        try :
            for i in range(len(performanceDetailList)) :
                # 파라미터에 들어갈 정보
                params = {  "key" : Config.GOOGLE_API_KEY,
                            "language" : "ko",
                            "radius" : 5000,
                            "keyword" : performanceDetailList[i][1] + ", " + performanceDetailList[i][2],
                            "location" : latitude+", "+longitude }
                # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
                res = requests.get(Config.GOOGLE_MAP_NEAR_BY_SEARCH_URL, params = params)
                res = res.json()
                # 5km 이내의 상영중인 시설만 리스트에 저장
                if res['status'] != "ZERO_RESULTS" :
                        print("place nearby")
                        nearByPlaceList.append(performanceDetailList[i])
        except Exception as e :
            print(e)

        return { "count" : len(nearByPlaceList), "resultList" : nearByPlaceList }, 200