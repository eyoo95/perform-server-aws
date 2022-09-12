# OpenAPI 이용하려면 requests 라이브러리 이용
import requests
from flask import request
from flask_restful import Resource
import xmltodict
import json
from config import Config
import mysql.connector
from mysql_connection import get_connection
from flask_jwt_extended import get_jwt_identity, jwt_required


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
        res = json.loads(json.dumps(xmlToJsonConverter))['dbs']

        if res is None :
            return { "resultList" : res }
        resultList = res['db']


        if len(resultList) == 9:
            extra_list = []
            extra_list.append(resultList)
            resultList = extra_list


        return { "resultList" : resultList }, 200



# 공연 상세 조회 (from DB)
class PerformanceDetailDBResource(Resource):
    @jwt_required()
    def get(self, prfId) :
        try :
            userId = get_jwt_identity()
            connection = get_connection()
            query = '''
                        select prf.*, count(pl.prfId) as likes, sum(ifnull(pv.viewCount,0)) as viewCount 
                        from prfViewCount pv
                        left join prfLike pl on pv.userId = pl.userId
                        left join prf on pv.prfId = prf.mt20id
                        where prf.mt20id = %s;
                    '''
            record = (prfId, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            resultList = cursor.fetchall()

            i = 0
            for record in resultList :
                resultList[i]['likes'] = int(record['likes'])
                resultList[i]['viewCount'] = int(record['viewCount'])+1
                i += 1
            
            # 조회수 확인
            query = ''' select * 
                    from prfViewCount 
                    where userId = {} and prfId = "{}"'''.format(userId, prfId)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query)
            resultList2 = cursor.fetchall()


            if resultList2 == []:
                try:
                    # 조회수 생성

                    query = '''insert into prfViewCount (userId, prfId) values ({}, "{}");'''.format(userId, prfId)
                    cursor = connection.cursor()
                    cursor.execute(query)
                    connection.commit()
                    

                except mysql.connector.Error as e :
                    print(e)

            # 조회수 증가
            query = '''update prfViewCount set viewCount = viewCount + 1 
                        where prfId = "{}"
                        and userId = {};'''.format(prfId, userId)

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

        res = json.loads(json.dumps(xmlToJsonConverter))['dbs']

        if res is None :
            return { "result" : res }
        resultList = res['db']


        return { "result" : resultList }, 200

    # 상세정보 볼 때 DB에 공연 정보 저장
    def post(self, prfId) :
        # 파라미터에 들어갈 정보
        params = { "service" : Config.KOPIS_ACCESS_KEY }

        # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
        response = requests.get(Config.KOPIS_PERFORMANCE_DETAIL_URL + prfId, params = params)

        # json 형태로 변환
        xmlToJsonConverter = xmltodict.parse(response.text)

        # json 타입으로 변경
        res = json.loads(json.dumps(xmlToJsonConverter))['dbs']

        if res is None :
            return { "result" : "현재 진행중인 공연이 없습니다."}
        resultList = res['db']

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
        res = json.loads(json.dumps(xmlToJsonConverter))['dbs']

        if res is None :
            return { "resultList" : res }
        resultList = res['db']

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
        res = json.loads(json.dumps(xmlToJsonConverter))['dbs']

        if res is None :
            return { "result" : res }
        resultList = res['db']
        
        return { "result" : resultList }, 200


# 내 지역(구) 공연 시설 조회
class NearByPerformanceResource(Resource) :
    def get(self, sidoCodeSub) :

        # 필수 파라미터
        stdate = request.args['stdate'] # 공연시작일자, 6자로 입력받기 ex) 20220701
        eddate = request.args['eddate'] # 공연종료일자, 6자로 입력받기 ex) 20220801
        cpage = request.args['cpage'] # 현재 페이지, 정수형으로 입력
        rows = request.args['rows'] # 페이지당 목록 수, 정수형으로 입력
        prfstate = request.args['prfstate'] # 공연 상태 코드

        signgucodesub = sidoCodeSub # 지역(시도) 코드

        # 내 지역 공연 조회 파라미터
        performanceSearchParams = { "service" : Config.KOPIS_ACCESS_KEY,
                                    "stdate" : stdate,
                                    "eddate" : eddate,
                                    "cpage" : cpage,
                                    "rows" : rows,
                                    "signgucodesub" : signgucodesub,
                                    "prfstate" : prfstate }

        # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
        response = requests.get(Config.KOPIS_PERFORMANCE_SERARCH_URL, params=performanceSearchParams)
        # json 형태로 변환
        xmlToJsonConverter = xmltodict.parse(response.text)
        # json 타입으로 변경
        res = json.loads(json.dumps(xmlToJsonConverter))['dbs']

        if res is None :
            return { "result" : res }
        performanceList = res['db']

        if len(performanceList) == 9:
            extra_list = []
            extra_list.append(performanceList)
            performanceList = extra_list
        # print(performanceList[0]['mt20id'])

        # 공연과 시설의 정보 저장
        # 공연 상세 조회 파라미터
        params = { "service" : Config.KOPIS_ACCESS_KEY }
        try : 
            resultList = []
            responseList = {}
            responseConverter = []
            tempList = []
            for i in range(len(performanceList)) :

                # 공연과 시설 정보 저장
                performanceDetailResponse = requests.get(Config.KOPIS_PERFORMANCE_DETAIL_URL + performanceList[i]['mt20id'], params = params)
                xmlToJsonConverter1 = xmltodict.parse(performanceDetailResponse.text)
                res1 = json.loads(json.dumps(xmlToJsonConverter1))['dbs']['db']

                placeResponse = requests.get(Config.KOPIS_PERFORMANCE_PLACE_DETAIL_URL + res1['mt10id'], params = params)
                xmlToJsonConverter2 = xmltodict.parse(placeResponse.text)
                res2 = json.loads(json.dumps(xmlToJsonConverter2))['dbs']['db']

                responseList['mt20id'] = res1['mt20id']
                responseList['prfnm'] = res1['prfnm']
                responseList['mt10id'] = res1['mt10id']
                responseList['fcltynm'] = res2['fcltynm']
                responseList['latitude'] = res2['la']
                responseList['longitude'] = res2['lo']

                responseConverter = list(responseList.values())

                tempList = {string : responseConverter[i] for i,string in enumerate(responseList)}

                resultList.append( tempList )

        except Exception as e :
            print(e)

        #print(tempList)
        return { "count" : len(resultList), "resultList" : resultList }, 200

# 반경 내 공연 Map 표시
class NearPerformanceResource(Resource) :
    def get(self):
        # 쿼리 스트링으로 오는 데이터는 아래처럼 처리한다.  
        
        latitude = request.args['latitude']
        longitude = request.args['longitude']
        distance = request.args['distance']
        isOpen = request.args['isOpen']

        # 공연 여부
        if isOpen == "open":
            isOpen = "and isOpen = 1"
        elif isOpen == "close":
            isOpen = "and isOpen = 0"
        elif isOpen == "all":
            isOpen =""


        try :
            connection = get_connection()

            query = '''set @location = point({}, {});'''.format(longitude, latitude)
            cursor = connection.cursor()
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()


            query = '''select prf.mt20id, pp.fcltynm, pp.mt10id, pp.mt13cnt, pp.fcltychartr, pp.opende , pp.seatscale , pp.telno , pp.relateurl , pp.adres , pp.la , pp.lo
                        , if(char_length(prf.prfstate)= 3,1,0) as isOpen
                        , st_distance_sphere(@location, latLng) as distance 
                        from prf
                        left join prfPlace pp on prf.mt10id = pp.mt10id
                        group by pp.mt10id having distance <= {} {}
                        order by distance asc, isOpen desc;'''. format(distance, isOpen)

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.
            cursor.execute(query )

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            resultList = cursor.fetchall()

            i = 0
            for record in resultList:
                resultList[i]['la'] = float(record['la'])
                resultList[i]['lo'] = float(record['lo'])
                resultList[i]['distance'] = float(record['distance'])
                i = i + 1
            

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e), 'error_no':20}, 503

        return { "result" : "success",
                "count" : len(resultList),
                "result" : resultList} , 200


# 공연 좋아요 추가 
class PerformanceLikeResource(Resource) :
    @jwt_required()
    def post(self, prfId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''insert into prfLike (userId, prfId) values (%s, %s);'''
            record = (userId, prfId)
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
    
    # 공연 좋아요 취소
    @jwt_required()
    def delete(self, prfId) :
        try :
            connection = get_connection()
            userId = get_jwt_identity()
            query = '''delete from prfLike where userId = %s and prfId = %s;'''
            record = (userId, prfId)
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

