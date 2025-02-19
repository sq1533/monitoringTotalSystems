import sys
import subprocess
import json
import pandas as pd
import time
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

from ..loadPath import loginInfoPath, restDayPath, rmMailPath

#재시작 프로토콜
def restart_script():
    driver.quit()
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit()

#JSON파일 읽어오기
with open(loginInfoPath, 'r', encoding='utf-8') as f:
    login_info = json.load(f)
with open(restDayPath,"r") as f:
    restday = json.load(f)

#필요 데이터 판다스 Series데이터 변경
works_login = pd.Series(login_info['worksMail'])
tele_bot = pd.Series(login_info['RMbot'])

#숫자 콤마넣기
def comma(x):
    return '{:,}'.format(round(x))

def reset() -> None:
    """
    매월 1일 RM한도 임시증액 데이터를 초기화
    'resets' 초기 데이터 dict자료형을 판다스를 통해 DataFrame생성 및 to_json을 통한 덮어쓰기
    """
    resets = {
        "상점ID":"T_ID",
        "상점명":"T_Name",
        "월한도":"1000000",
        "비고":""
    }
    pd.DataFrame(resets,index=[0]).to_json(rmMailPath,orient='records',force_ascii=False,indent=4)
    requests.get(f"https://api.telegram.org/bot{tele_bot['token']}/sendMessage?chat_id={tele_bot['chatId']}&text=초기화_완료")
    time.sleep(61)

def read_mail(soup):
    """
    한도증액이 불필요한 데이터 필터링
    HTML을 bs4로 읽어오고 그 안에 테이블(td) 태그에서 필요한 데이터 추출
    추출한 데이터의 DataFrame 생성 및 분류 조건에 따라 행을 drop하는 형식
    분류된 newdata를 DataFrame형식 리턴
    """
    ignoreName = ["이지피쥐","핀테크링크​","엘피엔지​","코리아결제시스템"]
    ignoreOrder = ["오프라인"]

    RM_market = soup.find_all('td')
    text_count = len(RM_market)
    i : int = 2
    j : int = 3
    k : int = 5
    l : int = 13
    marketID : list = []
    marketName : list = []
    marketPrice : list = []
    order : list = []

    while l < text_count:
        marketID.append(str(RM_market[i]).replace('<td>','').replace('</td>',''))
        marketName.append(str(RM_market[j]).replace('<td>','').replace('</td>',''))
        marketPrice.append(str(RM_market[k]).replace('<td>','').replace('</td>','').replace(',',''))
        order.append(str(RM_market[l]).replace('<td>','').replace('</td>',''))
        i = i + 14
        j = j + 14
        k = k + 14
        l = l + 14
        if l >= text_count:
            break

    newdata = pd.DataFrame(data={"상점ID":marketID,"상점명":marketName,"월한도":marketPrice,"비고":order})

    RM_month = pd.read_json(rmMailPath,orient='records',dtype={'상점ID':str,'상점명':str,'월한도':str,'비고':str})
    lastID = RM_month['상점ID'].tolist()

    for n in newdata.index.tolist():
        if any(nm in str(newdata.loc[n]["상점명"]) for nm in ignoreName):
            newdata.drop(n, inplace=True)
        elif any(ord in str(newdata.loc[n]["비고"]) for ord in ignoreOrder):
            newdata.drop(n, inplace=True)
        elif any(id == str(newdata.loc[n]["상점ID"]) for id in lastID):
            newdata.drop(n, inplace=True)
        else:
            pass
    return newdata

def getHome(page) -> None:
    """
    초기 페이지 진입 및 저장된 ID와 PW로 로그인하는 과정
    selenium ActionChains을 통한 데이터 값 삽입 및 클릭 움직임 구현
    """
    time.sleep(1)
    id_box = page.find_element(By.XPATH,'//input[@id="user_id"]')
    login_button_1 = page.find_element(By.XPATH,'//button[@id="loginStart"]')
    id = works_login['id']
    ActionChains(page).send_keys_to_element(id_box, '{}'.format(id)).click(login_button_1).perform()

    time.sleep(1)
    password_box = page.find_element(By.XPATH,'//input[@id="user_pwd"]')
    login_button_2 = page.find_element(By.XPATH,'//button[@id="loginBtn"]')
    password = works_login['pw']
    ActionChains(page).send_keys_to_element(password_box, '{}'.format(password)).click(login_button_2).perform()

    time.sleep(1)
    page.get("https://mail.worksmobile.com/#/my/102")

def newMail(page) -> None:
    """
    분류된 메일함에 신규 메일 유무 확인
    신규 메일 로드 버튼 클릭 > bs4 HTML추출 > notRead 요소 확인
    notRead 확인 및 notRead mail_title 클릭 구현
    함수 read_mail() 필터링 및 DataFrame 리턴값 유무 체크
    [1]empty > "증액 필요 가맹점 없음" telegram bot API 요청
    [2]not.empty > format 함수로 텍스트 정제 및 telegram bot API 요청
    API 요청 후 분류된 메일함 재호출
    """
    ActionChains(page).click(page.find_element(By.XPATH,'//button[@class="btn_refresh refreshAtList"]')).perform()
    time.sleep(1)
    mailHome_soup = BeautifulSoup(page.page_source,'html.parser')
    newMailCheck = mailHome_soup.find_all('li', attrs={'class':'notRead'})

    if newMailCheck:
        newMail = page.find_element(By.XPATH,"//li[contains(@class,'notRead')]//div[@class='mTitle']//strong[@class='mail_title']")
        ActionChains(page).click(newMail).perform()
        time.sleep(2)
        mail_soup = BeautifulSoup(page.page_source,'html.parser')

        if read_mail(mail_soup).empty:
            tell = "{일}일 {시간}시 증액 필요 가맹점 없음".format(일=datetime.now().day,시간=datetime.now().hour)
            requests.get(f"https://api.telegram.org/bot{tele_bot['token']}/sendMessage?chat_id={tele_bot['chatId']}&text={tell}")
            page.get("https://mail.worksmobile.com/#/my/102")
        else:
            for update in read_mail(mail_soup).index.tolist():
                tell = '{일}일 {시간}시 {상점명}[{상점ID}] 한도 증액필요\n월한도 {한도}원 / 증액 {증액}원'.format(
                    일=datetime.now().day,
                    시간=datetime.now().hour,
                    상점명=read_mail(mail_soup).loc[update]["상점명"],
                    상점ID=read_mail(mail_soup).loc[update]["상점ID"],
                    한도=comma(int(read_mail(mail_soup).loc[update]["월한도"])),
                    증액=comma(int(read_mail(mail_soup).loc[update]["월한도"])*120/100))
                requests.get(f"https://api.telegram.org/bot{tele_bot['token']}/sendMessage?chat_id={tele_bot['chatId']}&text={tell}")
                RM_month = pd.read_json(rmMailPath,orient='records',dtype={'상점ID':str,'상점명':str,'월한도':str,'비고':str})

                if update == read_mail(mail_soup).index.tolist()[-1]:
                    resurts = pd.concat([RM_month,read_mail(mail_soup)],ignore_index=True)
                    resurts.to_json(rmMailPath,orient='records',force_ascii=False,indent=4)
                else:
                    pass

            page.get("https://mail.worksmobile.com/#/my/102")
    else:
        pass

def emailClick(page) -> None:
    """
    영업시간의 경우 서비스관리팀 미진행
    신규 메일 클릭 구현
    (newMail()함수는 notRead 요소를 모두 확인하기 때문에 읽지않은 메일 해소를 위함)
    """
    ActionChains(page).click(page.find_element(By.XPATH,'//button[@class="btn_refresh refreshAtList"]')).perform()
    time.sleep(1)

    mailHome_soup = BeautifulSoup(page.page_source,'html.parser')
    newMailCheck = mailHome_soup.find_all('li', attrs={'class':'notRead'})

    if newMailCheck:
        newMail = page.find_element(By.XPATH,"//li[contains(@class,'notRead')]//div[@class='mTitle']//strong[@class='mail_title']")
        ActionChains(page).click(newMail).perform()
        page.get("https://mail.worksmobile.com/#/my/102")
    else:
        pass

#영업일, 비영업일 구분
workTime = ["08:00","10:00","12:00","14:00","16:00"]
restTime = ["00:00","02:00","04:00","06:00","18:00","20:00","22:00"]

#크롬 드라이버 옵션값 설정
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
driver = webdriver.Chrome(options=options)
driver.get("https://mail.worksmobile.com/")
getHome(driver)

def main():
    """
    구동 스케쥴러 관리
    영업일 및 비영업일 구분
    try, except를 활용 및 subproccess 스크립트 재실행 구현
    """
    try:
        today = datetime.now()
        #데이터 리셋
        if today.strftime('%d %H:%M') == "01 01:00":
            reset()
        else:
            pass

        #영업일 구분
        if (today.weekday() == 5) or (today.weekday() == 6) or (today.strftime('%d') in restday[today.strftime('%m')]):
            if today.strftime('%H:%M') in list(set(workTime)|set(restTime)):
                for i in range(10):
                    newMail(driver)
                    time.sleep(3)
                time.sleep(3000)
            else:
                pass
        else:
            if today.strftime('%H:%M') in workTime:
                for i in range(10):
                    emailClick(driver)
                    time.sleep(3)
                time.sleep(3000)
            elif today.strftime('%H:%M') in restTime:
                for i in range(10):
                    newMail(driver)
                    time.sleep(3)
                time.sleep(3000)
            else:
                pass
        time.sleep(0.5)
    except Exception:
        driver.quit()
        time.sleep(2)
        restart_script()

if __name__ == "__main__":
    while True:
        try:
            main()
            time.sleep(0.1)
        except Exception as e:
            print(e)
            time.sleep(2)