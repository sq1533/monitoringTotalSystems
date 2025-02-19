import pandas as pd
import time
import pyautogui

from monitoringTotalSystems.loadPath import triggerPath, hotLineTriggerPath

#Global 대기시간 설정
pyautogui.PAUSE = 0.5

#핫라인 전파
def hotLine(pressKey=int) -> None:
    """
    핫라인 전파를 위한 카카오톡 핸들링
    핫라인 즐겨찾기 등록 및 제일 상단 핫라인 좌표값 입력
    키 down을 이용한 핫라인 변경
    키 down횟수는 함수 매개변수
    """
    time.sleep(0.5)
    pyautogui.click(x=20,y=20,clicks=1,button="left")
    pyautogui.click(x=400,y=215,clicks=1,button="left")
    pyautogui.press("down",presses=pressKey)
    pyautogui.press("enter")
    pyautogui.hotkey('ctrl','v')
    pyautogui.press("enter")
    pyautogui.press("esc")

if __name__ == "__main__":
    while True:
        time.sleep(0.2)
        startPoint = pd.read_json(triggerPath,orient='records')
        if startPoint['hotline'].tolist()[0] == 'start':
            pressDown = pd.read_json(hotLineTriggerPath)[0].values.tolist()
            for i in pressDown:
                hotLine(i)
            pd.DataFrame({"coochip":"end","enMail":"end","hotline":"end"},index=[0]).to_json(triggerPath,orient='records',force_ascii=False,indent=4)
            time.sleep(1)
        else:
            pass