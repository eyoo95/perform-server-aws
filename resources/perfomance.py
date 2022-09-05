# OpenAPI 이용하려면 requests 라이브러리 이용
import requests

from flask import request
from flask_restful import Resource
import xmltodict
import json
from config import Config

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
        resultList = json.loads(json.dumps(xmlToJsonConverter))

        return { "resultList" : resultList['dbs']['db'] }, 200

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
        resultList = json.loads(json.dumps(xmlToJsonConverter))

        return { "resultList" : resultList['dbs']['db'] }, 200

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
        resultList = json.loads(json.dumps(xmlToJsonConverter))

        return { "resultList" : resultList['dbs']['db'] }, 200

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
        resultList = json.loads(json.dumps(xmlToJsonConverter))

        return { "resultList" : resultList['dbs']['db'] }, 200

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