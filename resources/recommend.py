import requests
from flask import request
from flask_restful import Resource
import xmltodict
import json
from config import Config
import pandas as pd 
from flask_restful import Resource
from mysql.connector.errors import Error
from mysql_connection import get_connection
from flask_jwt_extended import get_jwt_identity, jwt_required
import mysql.connector

# 실시간 영화 개인화 추천 API
class PerformaceRecomRealTimeRersource(Resource):
    @jwt_required()
    def get(self) :
        # 클라이언트로부터 데이터를 받아온다.
        userId = get_jwt_identity()

        # 유저의 별점 정보를 DB에서 가져온다.
        try :
            connection = get_connection()

            ####
            query = '''select pr.userId, pr.prfId, pr.rating, prf.prfnm as title
                        from prfRating pr
                        join prf
                        on prf.mt20id = pr.prfId;'''


            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query)

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            resultList = cursor.fetchall()

            print(resultList)

            df = pd.DataFrame(data= resultList)

            print(df)


            matrix = df.pivot_table(index='userId', columns='title',values='rating')

            print(matrix)

            df = matrix.corr() # min_periods=50

            print(df)
            #####

            query = '''select pr.userId, pr.prfId, prf.prfnm as title, pr.rating
                        from prfRating pr
                        join prf
                        on pr.prfId = prf.mt20id and pr.userId = %s;'''

            record = (userId,)

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.

            cursor.execute(query, record)

            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            resultList = cursor.fetchall()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e), 'error_no':20}, 503

        # 가져온 유저 개인 rating 데이터를 데이터프레임으로 만든다.
        dfMyRating = pd.DataFrame(data = resultList)

        print(dfMyRating)

        # 추천 영화를 저장할 빈 데이터 프레임을 만든다.
        similarPrfList = pd.DataFrame()

        for i in range(len(dfMyRating)):
            similarPrf = df[dfMyRating['title'][i]].dropna().sort_values(ascending=False).to_frame()
            similarPrf.columns = ['Correlation']
            similarPrf['Weight'] = dfMyRating['rating'][i] * similarPrf['Correlation']
            similarPrfList = similarPrfList.append(similarPrf)

        # 중복된 영화가 있을수있다. 중복된영화는 weight가 가장 큰 값으로 해준다.
        similarPrfList.reset_index(inplace=True)
        similarPrfList = similarPrfList.groupby('title')['Weight'].max().sort_values(ascending=False)

        # 내가 이미 봐서 별점을 남긴 영화는 제외해야한다.
        similarPrfList = similarPrfList.reset_index()

        # 내가 이미 본 영화제목만 가져온다.
        titleList = dfMyRating['title'].tolist()

        # similarPrfList에 내가 본영화인 titleList를 제외하고 가져온다.
        # similarPrfList['title'].isin(titleList)
        recommendPrfList = similarPrfList.loc[ ~similarPrfList['title'].isin(titleList), ]

        return { "result" : "success",
                "prfList" : recommendPrfList.iloc[0:20,].to_dict('records')} , 200

class myInterestingPerformanceTop3Resource(Resource) :
    def get(self, prfId1, prfId2, prfId3) :
        # 파라미터에 들어갈 정보
        params = { "service" : Config.KOPIS_ACCESS_KEY }

        prfId = [ prfId1, prfId2, prfId3 ]
        resultList = []

        for i in prfId :
            # 요청하는 API의 URL과 API에서 요구하는 데이터 입력
            response = requests.get(Config.KOPIS_PERFORMANCE_DETAIL_URL + i, params = params)

            # json 형태로 변환
            xmlToJsonConverter = xmltodict.parse(response.text)
            res = json.loads(json.dumps(xmlToJsonConverter))['dbs']['db']

            resultList.append(res)

        return { "resultList" : resultList }, 200