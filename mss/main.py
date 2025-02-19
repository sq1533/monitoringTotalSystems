import os
import pandas as pd
import re
import datetime
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import database
from monitoringTotalSystems.loadPath import midInfoPath

#AI_MON simple 알람 타켓
target_simple = [':거래없음',':거래감소',':거래(성공건)없음',':거래급증',':거래(오류)급증',':성공율 하락',':비정상환불',':비정상취소']
#AI_MON error 알람 타켓
target_error = [':동일오류',':오류발생']

app = FastAPI()

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__),"templates"))

#URL 정제
def urls_to_links(text):
    url = r'(https?://[^\s<]+)'
    return re.sub(url,r'<a href="\1" target="_blank">\1</a>',text)

@app.get("/home",response_class=HTMLResponse)
async def home(request:Request):
    """
    Jinja를 활용한 템플릿 호출
    Request를 이용하여 .templates/home.html 웹서버 반영
    """
    return templates.TemplateResponse("home.html",{"request":request})

@app.get("/alarm_{number}")
def alarm_1(number:int):
    """
    Alarm.json파일 호출 및 number변수 index행 호출
    알람에 확인 유무를 판단하기 위한 form > button HTML 호출
    Alarm.json파일 alarm 구분값 확인을 위한 target리스트를 기준으로 분류 및 string데이터 split()
    구분값은 midInfo.json파일['mid'] 일치 값 정보 호출
    HTMLresponse를 이용하여 HTML값 전송
    """
    info = pd.read_json(midInfoPath,orient="records",dtype={"mid":str,"info":str})
    midList = info['mid'].tolist()

    alarmPath = os.path.join(os.path.dirname(__file__),"..","DB","Alarm",f"worksAlarm_{datetime.date.today().strftime("%y%m%d")}.json")
    alarm = pd.read_json(alarmPath,orient="records",dtype={"Alarm":str,"date":str,"check":str})
    #알람
    alarmData = urls_to_links(alarm.iloc[number]['Alarm'])
    #알람 정제 및 구분값 확인
    if any(i in alarmData for i in target_simple):
        MID_1 = alarmData.split('가맹점:')[1]
        MID_2 = MID_1.split('[',1)[1]
        MID = MID_2.split(']',1)[0]
        alarmAF = {"Alarm":alarmData,"mid":MID}
    elif any(i in alarmData for i in target_error):
        AI = alarmData.replace(' ','')
        MID_1 = AI.split('오류코드:')[1]
        code = str(MID_1.split('(',1)[0])
        alarmAF = {"Alarm":alarmData,"mid":code}
    else:
        alarmAF = {"Alarm":alarmData,"mid":"None"}
    #구분값 확인 및 midInfo 비교
    if alarmAF["mid"] in midList:
        midInfo = urls_to_links(info[info['mid'].isin([alarmAF['mid']])]['info'].reset_index(drop=True)[0])
    else:
        midInfo = str(f"{alarmAF['mid']} DB생성 필요")
    #알람 처리 로직 설정
    checkPoint = alarm.iloc[number]['check']
    if checkPoint == "nonCheck":
        checkMessage = f"""
            <form class="text-base" hx-post="/alarmCheck{number}" hx-target="#callResults{number}" hx-swap="innerHTML" hx-boost="true">
                <button class="w-1/4 rounded-lg bg-green-300 font-bold text-black hover:bg-green-500" type="submit" name="results" value="특이사항 없음">특이사항 없음</button>
                <button class="w-1/4 rounded-lg bg-green-300 font-bold text-black hover:bg-green-500" type="submit" name="results" value="게시판">게시판</button>
                <div id="callResults{number}"></div>
            </form>
            """
    elif checkPoint == "게시판":
        checkMessage = "<div class='font-bold text-lg text-red-600'>게시판 작성</div>"
    else:
        checkMessage = "<div class='font-bold text-lg text-blue-400'>완료</div>"
    #최종 알람 데이터 생성
    html = f"""
            <div id="alarm{number}">{alarmData}</div>
            <button id="alarm6Copy" class="w-full rounded-lg font-bold text-white bg-blue-500" onclick="copyText('alarm{number}')">알람 복사</button><br><br>
            {midInfo}<br><br>
            {checkMessage}
            <script>
            function copyText(elementId) {{
                var textElement = document.getElementById(elementId);
                var tempTextArea = document.createElement("textarea");
                tempTextArea.value = textElement.innerText;
                document.body.appendChild(tempTextArea);
                tempTextArea.select();
                document.execCommand("copy");
                document.body.removeChild(tempTextArea);
            }};
            </script>
            """
    return HTMLResponse(content=html)

@app.post("/alarmCheck{number}")
async def result(number:int,request:Request):
    """
    form > button 알람확인 유무 체크 값 post
    해당 알람에 [check]컬럼값 post 값으로 변경
    check컬럼 group화 및 각 group의 date컬럼 내림차순 진행
    변경된 DataFrame 기존 json에 덮어쓰기
    """
    data = await request.form()
    alarmPath = os.path.join(os.path.dirname(__file__),"Alarm",f"worksAlarm_{datetime.date.today().strftime("%y%m%d")}.json")
    alarm = pd.read_json(alarmPath,orient="records",dtype={"Alarm":str,"date":str,"check":str})
    alarm.loc[number]['check'] = data["results"]
    grouping = alarm.groupby('check')
    alarmResults = grouping.apply(lambda x: x.sort_values(by='date',ascending=False)).reset_index(drop=True)
    alarmResults.to_json(alarmPath,orient='records',force_ascii=False,indent=4)
    return HTMLResponse(content="제출 완료")

@app.post("/allCheck")
async def result(request:Request):
    """
    [check]컬럼값 post 값으로 모두 변경
    check컬럼 group화 및 각 group의 date컬럼 내림차순 진행
    변경된 DataFrame 기존 json에 덮어쓰기
    """
    data = await request.form()
    alarmPath = os.path.join(os.path.dirname(__file__),"Alarm",f"worksAlarm_{datetime.date.today().strftime("%y%m%d")}.json")
    alarm = pd.read_json(alarmPath,orient="records",dtype={"Alarm":str,"date":str,"check":str})
    alarm["check"] = alarm["check"].replace("nonCheck",data["check"])
    alarmResults = alarm.sort_values(by='date',ascending=False).reset_index(drop=True)
    alarmResults.to_json(alarmPath,orient='records',force_ascii=False,indent=4)
    return HTMLResponse(content="제출 완료")

#데이터 설정
class mk(BaseModel):
    mid : str
    info : str

class mid(BaseModel):
    mid : str

class mail(BaseModel):
    passnumber : str
    addr : str
    subaddr : str
    title : str
    main : str

#생성
@app.post("/mk_info")
async def create(response: mk):
    database.cre(dict(response))

#수정
@app.put("/mk_info")
async def change(response: mk):
    database.put(dict(response))

#삭제
@app.post("/mk_info_d")
async def delete(response: mid):
    database.delete(dict(response))

#트리거 메일영문
@app.post("/triggere")
async def triggerE():
    database.TriggerMail1()

#트리거 메일쿠칩
@app.post("/triggerc")
async def triggerC():
    database.TriggerMail2()

#트리거 핫라인
@app.post("/hotline")
async def hotLine():
    database.hotLine()

#메일전송
@app.post("/email")
async def sendMail(response: mail):
    database.mail(dict(response))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8502)