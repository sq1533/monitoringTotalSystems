import json
import pandas as pd
import time
import requests

from ...loadPath import loginInfoPath, triggerPath, mailTriggerPath

def ezMail(id:str,pw:str,botAPI:str,botID:str) -> None:
    """
    selenium ActionChains ID/PW입력 및 메일 입력값 기입
    구동 trigger 발동 시 크롬 드라이버를 통한 네이버 웍스 로그인, 인증값 대기상태(800번 호출)
    메일 입력값 trigger에 검증값(passingumber)확인 == isdigit()함수를 통한 숫자데이터 유무 확인
    인증 완료 후 메일 작성창 호출 및 입력값, 입력요소에 기입
    구동 완료 후 resets데이터 덮어쓰기
    """
    from selenium import webdriver
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By

    #크롬 옵션설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-javascript")
    options.add_argument('--disable-extensions')
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=options)

    url = "https://auth.worksmobile.com/login/login?accessUrl=https%3A%2F%2Fmail.worksmobile.com%2F"
    driver.get(url)
    driver.implicitly_wait(1)

    id_box = driver.find_element(By.XPATH,'//input[@id="user_id"]')
    login_button_1 = driver.find_element(By.XPATH,'//button[@id="loginStart"]')
    ActionChains(driver).send_keys_to_element(id_box, '{}'.format(id)).click(login_button_1).perform()
    time.sleep(1)

    password_box = driver.find_element(By.XPATH,'//input[@id="user_pwd"]')
    login_button_2 = driver.find_element(By.XPATH,'//button[@id="loginBtn"]')
    ActionChains(driver).send_keys_to_element(password_box, '{}'.format(pw)).click(login_button_2).perform()
    time.sleep(1)

    passingMail = driver.find_element(By.XPATH,'//a[@id="privateEmailButton"]')
    ActionChains(driver).click(passingMail).perform()
    time.sleep(5)

    while True:
        for i in range(800):
            mail = pd.read_json(mailTriggerPath,orient='records',dtype={"passnumber":str,"addr":str,"subaddr":str,"title":str,"main":str})
            passingnumber = mail['passnumber'].tolist()[-1]
            #인증번호 검증
            if passingnumber.isdigit():
                passingN = driver.find_element(By.XPATH,'//input[@id="number1"]')
                ActionChains(driver).click(passingN).send_keys('{}'.format(passingnumber)).perform()
                time.sleep(1)
                driver.get('https://mail.worksmobile.com/#/compose?orderType=new')
                time.sleep(1)
                driver.maximize_window()
                time.sleep(1)

                mailHome = driver.find_elements(By.XPATH, '//input[@aria-label="받는사람"]')
                if mailHome:
                    address = driver.find_element(By.XPATH,'//input[@aria-label="받는사람"]')#수신자 입력창
                    subaddress = driver.find_element(By.XPATH,'//input[@aria-label="참조"]')#참조 입력창
                    mailtitle = driver.find_element(By.XPATH,'//input[@aria-label="제목"]')#제목 입력창
                    mailmain = driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div[3]/div[2]/div/fieldset/div/div/div/div[3]')#내용 입력창
                    send_button = driver.find_element(By.XPATH,'//button[@data-hotkey="sendKey"]')#전송 버튼
                    send_each = driver.find_element(By.XPATH,'//input[@name="sendSeparately"]')#개인별 체크박스

                    #메일내용 입력
                    mmain = mail['main'].tolist()[-1]
                    ActionChains(driver).click(mailmain).send_keys(Keys.PAGE_UP).send_keys('{}'.format(mmain)).perform()
                    time.sleep(1)

                    #메일제목 입력
                    mtitle = mail['title'].tolist()[-1]
                    ActionChains(driver).click(mailtitle).send_keys_to_element(mailtitle,'{}'.format(mtitle)).perform()
                    time.sleep(1)

                    #참조 입력
                    subaddrs = mail['subaddr'].tolist()[-1]
                    ActionChains(driver).send_keys_to_element(subaddress, '{}'.format(subaddrs)).perform()
                    time.sleep(1)

                    #수신자 입력
                    addrs = mail['addr'].tolist()[-1]
                    ActionChains(driver).send_keys_to_element(address, '{}'.format(addrs)).perform()
                    time.sleep(1)

                    #개인별 전송 클릭
                    ActionChains(driver).click(send_each).perform()
                    time.sleep(1)

                    #전송 클릭_1
                    ActionChains(driver).click(send_button).perform()
                    time.sleep(5)

                    """
                    #전송 클릭_2
                    send_button = driver.find_element(By.XPATH,'/html/body/div[3]/div/div/div/h3/div/button[1]')
                    ActionChains(driver).click(send_button).perform()
                    time.sleep(5)
                    """
                    driver.quit()

                    requests.get(f"https://api.telegram.org/bot{botAPI}/sendMessage?chat_id={botID}&text=메일전송 성공")
                    time.sleep(1)
                    break

                else:
                    driver.quit()

                    requests.get(f"https://api.telegram.org/bot{botAPI}/sendMessage?chat_id={botID}&text=인증실패, 재시도 요망")
                    time.sleep(1)
                    break
            else:
                time.sleep(0.5)
                pass

        mailReset = {"passnumber":"test","addr":"test_a","subaddr":"test_s","title":"test_t","main":"test_m"}
        pd.DataFrame(mailReset,index=[0]).to_json(mailTriggerPath,orient='records',force_ascii=False,indent=4)
        requests.get(f"https://api.telegram.org/bot{botAPI}/sendMessage?chat_id={botID}&text=초기화 완료")
        break

if __name__ == "__main__":
    while True:
        #로그인 및 시작 정보 확인
        with open(loginInfoPath,'r',encoding='utf-8') as f:
            loginInfo = json.load(f)

        enMail = pd.Series(loginInfo["enMail"])
        coochip = pd.Series(loginInfo["coochip"])
        bot = pd.Series(loginInfo["ezmailbot"])

        startPoint = pd.read_json(triggerPath,orient='records')

        if startPoint['coochip'].tolist()[0] == 'start':
            ezMail(coochip['id'],coochip['pw'],bot['token'],bot['chatId'])
            pd.DataFrame({"coochip":"end","enMail":"end","hotline":"end"},index=[0]).to_json(triggerPath,orient='records',force_ascii=False,indent=4)
            time.sleep(1)

        elif startPoint['enMail'].tolist()[0] == 'start':
            ezMail(enMail['id'],enMail['pw'],bot['token'],bot['chatId'])
            pd.DataFrame({"coochip":"end","enMail":"end","hotline":"end"},index=[0]).to_json(triggerPath,orient='records',force_ascii=False,indent=4)
            time.sleep(1)

        else:
            time.sleep(1)
            pass