import json
import pandas as pd
import requests
import time
from datetime import datetime

from monitoringTotalSystems.loadPath import loginInfoPath, restDayPath, reMindPath

with open(loginInfoPath, 'r', encoding='utf-8') as f:
    login_info = json.load(f)
with open(restDayPath,"r") as f:
    restday = json.load(f)

bot_info = pd.Series(login_info['nFaxbot'])
bot_HC = pd.Series(login_info['nFaxbot_hc'])

#리마인드
def reMind() -> None:
    today = datetime.now()

    #공휴일 리마인드 발송 제외
    if (today.weekday() == 5) or (today.weekday() == 6) or (today.strftime('%d') in restday[today.strftime('%m')]):
        time.sleep(36000)
        pass
    else:
        if today.strftime("%H:%M") == "09:00":
            read = pd.read_json(reMindPath,orient='records',dtype={"sendDay":str,"inputBank":str,"sendBank":str,"cost":str,"comments":str})

            if len(read.index.tolist()) == 1:
                pass
            else:
                for i in read["sendDay"].tolist():
                    if i == "test":
                        pass
                    elif i == today.strftime("%m-%d"):
                        pass
                    else:
                        ID = read[read["sendDay"].isin([i])].index.tolist()[0]
                        sendText = f"발송날짜 : {read.loc[ID]["sendDay"]}\n입금 은행 : {read.loc[ID]["inputBank"]}\n발송한 은행 : {read.loc[ID]["sendBank"]}\n피해금액 : {read.loc[ID]["cost"]}\n{read.loc[ID]["comments"]}"
                        requests.get(f"https://api.telegram.org/bot{bot_info['token']}/sendMessage?chat_id={bot_info['chatId']}&text={sendText}")
                        read.drop(ID, inplace=True)
                        time.sleep(1)

                #발송 후 데이터 리셋
                read.to_json(reMindPath,orient='records',force_ascii=False,indent=4)
                requests.get(f"https://api.telegram.org/bot{bot_HC['token']}/sendMessage?chat_id={bot_HC['chatId']}&text=리마인드 전송 및 리셋")
                time.sleep(60)
        else:
            time.sleep(30)
            pass

if __name__ == "__main__":
    while True:
        reMind()