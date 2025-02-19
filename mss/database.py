import pandas as pd

from monitoringTotalSystems.loadPath import triggerPath, midInfoPath, mailTriggerPath

def cre(data):
    """
    DB 구분자 및 정보 생성
    read_json()실행, new dict데이터 DataFrame 변경 및 병합
    to_json() 기존 데이터 덮어쓰기
    """
    DF = pd.read_json(midInfoPath,orient='records',dtype={'mid':str,'info':str})
    new = {
        "mid":data['mid'],
        "info":data['info']
        }
    new_df = pd.DataFrame(new,index=[0])
    resurts = pd.concat([DF,new_df],ignore_index=True)
    return resurts.to_json(midInfoPath,orient='records',force_ascii=False,indent=4)

def put(data):
    """
    read_json()실행, 입력값과 일치하는 구분자의 [info]데이터를 입력값의 [info]데이터로 변경
    to_json() 기존 데이터 덮어쓰기
    """
    DF = pd.read_json(midInfoPath,orient='records',dtype={'mid':str,'info':str})
    chn = {
        "mid":data['mid'],
        "info":data['info']
        }
    DF.loc[DF['mid']==chn['mid'],'info'] = chn['info']
    return DF.to_json(midInfoPath,orient='records',force_ascii=False,indent=4)

def delete(data):
    """
    read_json()실행, 입력값과 일치하는 구분자의 index값 호출
    기존 데이터의 index drop진행
    to_json() 기존 데이터 덮어쓰기
    """
    DF = pd.read_json(midInfoPath,orient='records',dtype={'mid':str,'info':str})
    d = {
        "mid":data['mid']
        }
    ind = DF[DF['mid']==d['mid']].index
    DF.drop(ind, inplace=True)
    return DF.to_json(midInfoPath,orient='records',force_ascii=False,indent=4)

def TriggerMail1():
    """
    트리거 파일 전송
    쿠칩 start
    """
    return pd.DataFrame({"coochip":"start","enMail":"end","hotline":"end"},index=[0]).to_json(triggerPath,orient='records',force_ascii=False,indent=4)

def TriggerMail2():
    """
    트리거 파일 전송
    영문메일 start
    """
    return pd.DataFrame({"coochip":"end","enMail":"start","hotline":"end"},index=[0]).to_json(triggerPath,orient='records',force_ascii=False,indent=4)

def hotLine():
    """
    트리거 파일 전송
    hotLine start
    """
    return pd.DataFrame({"coochip":"end","enMail":"end","hotline":"start"},index=[0]).to_json(triggerPath,orient='records',force_ascii=False,indent=4)

def mail(data):
    """
    트리거 파일 전송
    메일 입력값 덮어쓰기(쿠칩 및 영문메일)
    """
    email = {
        "passnumber":data["passnumber"],
        "addr":data["addr"],
        "subaddr":data["subaddr"],
        "title":data["title"],
        "main":data["main"]
        }
    PN = pd.DataFrame(email,index=[0])
    return PN.to_json(mailTriggerPath,orient='records',force_ascii=False,indent=4)