from flask import request
from flask_restful import Resource
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
        userId = get_jwt_identity()
        limit = request.args['limit']
        offset = request.args['offset']

        try :
            connection = get_connection()
            # 유저의 별점 정보를 DB에서 가져온다.
            query = '''select pr.userId, pr.prfId, pr.rating
                        from prfRating pr
                        join prf
                        on prf.mt20id = pr.prfId;'''
            cursor = connection.cursor(dictionary = True) 
            cursor.execute(query)
            resultList = cursor.fetchall()
            cursor.close()
            # 별점 정보
            dfPrfRating = pd.DataFrame(data= resultList)
            # 상연되고 있거나 별점이 있는 공연 정보
            query = '''select prf.mt20id as prfId
                        , if(char_length(prfstate)= 3,1,0) as isOpen, ifnull(count(pr.prfId),0) as countRating
                        from prf
                        left join prfRating pr on prf.mt20id = pr.prfId
                        group by prf.mt20id having isOpen = 1 or countRating > 0
                        order by isOpen desc, countRating desc;'''
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query)
            resultList = cursor.fetchall()
            cursor.close()
            # 유효한 공연 정보
            dfPrf = pd.DataFrame(data = resultList).drop("isOpen", axis=1).drop("countRating",axis=1)

            # 별점, 공연 데이터프레임 합치기
            dfPrf = pd.merge(dfPrfRating,dfPrf,on= 'prfId')
            # 피봇테이블 만들기
            matrix = dfPrf.pivot_table(index='userId', columns = 'prfId', values='rating')
            # correlation으로 관계값 찾기
            df = matrix.corr() # 데이터가 어느정도 쌓이면 최소값을 조정

            print(df)

            #####

            # 내 별점 리스트 가져오기
            query = '''select pr.userId, pr.prfId, pr.rating
                        from prfRating pr
                        left join prf
                        on pr.prfId = prf.mt20id
                        where pr.userId = %s;'''
            record = (userId,)
            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.
            cursor.execute(query, record)
            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            resultList = cursor.fetchall()
            cursor.close()


            # 가져온 유저 개인 rating 데이터를 데이터프레임으로 만든다.
            dfMyRating = pd.DataFrame(data = resultList)

            # 추천 영화를 저장할 빈 데이터 프레임을 만든다.
            similarPrfList = pd.DataFrame()

            for i in range(len(dfMyRating)):
                similarPrf = df[dfMyRating['prfId'][i]].dropna().sort_values(ascending=False).to_frame()
                similarPrf.columns = ['Correlation']
                similarPrf['Weight'] = dfMyRating['rating'][i] * similarPrf['Correlation']
                similarPrfList = pd.concat([similarPrfList,similarPrf])


            # 중복된 영화가 있을수있다. 중복된영화는 weight가 가장 큰 값으로 해준다.
            similarPrfList.reset_index(inplace=True)
            recommendPrfList = similarPrfList.groupby('prfId')['Weight'].max().sort_values(ascending=False)


# 데이터가 어느정도 쌓이면 아래의 주석을 푸는걸로 합니다.

#             # 내가 이미 봐서 별점을 남긴 영화는 제외해야한다.
#             similarPrfList = similarPrfList.reset_index()

#             # 내가 이미 본 영화제목만 가져온다.
#             titleList = dfMyRating['title'].tolist()

#             print(titleList)

#             # similarPrfList에 내가 본영화인 titleList를 제외하고 가져온다.
#             similarPrfList['title'].isin(titleList)
#             recommendPrfList = similarPrfList.loc[ ~similarPrfList['title'].isin(titleList), ]

#             print(recommendPrfList)

            recommendPrfList = recommendPrfList.iloc[0:10,].reset_index().to_dict("records")

            # 쿼리문에 넣을 prfId 문자열 처리
            recomPrfIdStr = ""
            if len(recommendPrfList) == 1:
                recomPrfIdStr = recomPrfIdStr +"mt20id = '"+ recommendPrfList[0]["prfId"]+"'"
            elif len(recommendPrfList) > 1:
                for i in range(len(recommendPrfList)-1):
                    recomPrfIdStr = recomPrfIdStr +"mt20id = '"+ recommendPrfList[i]["prfId"]+"'"+" or "
                recomPrfIdStr = recomPrfIdStr +"mt20id = '"+ recommendPrfList[-1]["prfId"]+"'"
            elif len(recommendPrfList) < 1:
                recommendPrfList = None
                return{ "resultList" : None }, 200


            # 해당 prfId를 가져와 추천할 prf 가져오기
            query = '''
                        select mt20id, prfnm, prfpdfrom, prfpdto, fcltynm, poster, genrenm, prfstate, openrun
                        from prf
                        where {}
                        order by prfpdfrom desc
                        limit {} offset {};
                    '''.format(recomPrfIdStr, limit, offset)

            # select 문은 dictionary = True를 해준다.
            cursor = connection.cursor(dictionary = True)  # 데이터를 셀렉할때 키벨류로 가져온다.
            cursor.execute(query)
            # select문은 아래 함수를 이용해서 데이터를 가져온다.
            resultList = cursor.fetchall()
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error":str(e), 'error_no':20}, 503



        return { "resultList" : resultList },200
