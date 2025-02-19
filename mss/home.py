import requests
import json
import pandas as pd
import time
import clipboard
import streamlit as st
import streamlit.components.v1 as components

from ..loadPath import loginInfoPath, midInfoPath, hotLineTriggerPath, otherMattersPath

#streamlit UI css변경
st.markdown(
"""
<style>
    .stAppHeader {
        visibility: visible;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
</style>
""",unsafe_allow_html=True,)

#핫라인 구동 trigger 실행
hotline = "http://127.0.0.1:8501/hotline"
def hotLine():
    requests.post(hotline)

#호출 json데이터 읽기
with open(loginInfoPath, 'r', encoding="UTF-8") as f:
    login_DB = json.load(f)
with open(otherMattersPath,'r',encoding="UTF-8") as f:
    order = json.load(f)

#streamlit components을 통한 웹서버 호출 IP 설정
url = login_DB['IP']['IP']+"/home"

def H_page() -> None:
    """
    main.py Fast API 구축 웹서버 호출
    조회 기능 구현(입력값과 midInfo 구분값 일치 유무 확인 및 일치 데이터 호출)
    주요 서버 데이터 st.selectbox에 삽입
    hotLine 간편전송 2가지 모델 설정
    1. 원천사 이슈 원천사에 부여된 리스트 데이터 호출 및 hotLineTrigger로 전송
    2. text_input()으로 입력된 데이터값 복사 및 체크박스가 적용된 알람방 hotLineTrigger 전송
    """
    midInfo = pd.read_json(midInfoPath,orient="records",dtype={"mid":str,"info":str})
    midList = midInfo['mid'].tolist()

    left, right = st.columns([2,1], vertical_alignment="top")
    with left.expander(label="조회",expanded=False):
        mid = st.text_input("MID조회(입력 후 Enter)")
        if st.button("조회") or mid:
            if mid in midList:
                st.write(midInfo.loc[midInfo['mid']==mid]['info'].tolist()[0].replace("<br>","  \n"))
            else:
                st.write('존재하지 않는 MID입니다.')

    #주요 서버 목록
    with right.expander(label="서버목록",expanded=False):
        svr = st.selectbox("주요 서버 목록",order["server"],index=None)
        st.code(svr)

    #실시간 알람 불러오기
    components.iframe(url,width=650,height=5000)
    #핫라인 사이드바
    with st.sidebar:
        stoKey = st.selectbox("원천사 이슈 전파",list(order['hotLine'].keys()))
        line = order["hotLine"][stoKey]
        ment = st.radio("장애내용",("지연중입니다.","간헐적 지연중입니다.","개시지연중입니다.","정상화 되었습니다."))
        fixed = stoKey+' '+ment

        if st.button("장애전파"):
            if stoKey == "선택":
                st.error("공유될 원천사 정보 없음")
            else:
                clipboard.copy(fixed)
                pd.DataFrame(line).to_json(hotLineTriggerPath,orient='columns',force_ascii=False,indent=4)
                hotLine()

                with st.spinner('구동중입니다.'):
                    time.sleep(4)
                    st.success('핫라인을 확인해주세요.')

        coor = []
        unfixed = st.text_input("핫라인 전파")

        if st.checkbox("쿠팡",value=True):coor.append(0)
        if st.checkbox("카카오페이",value=True):coor.append(1)
        if st.checkbox("카카오모빌리티",value=True):coor.append(2)
        if st.checkbox("네이버페이",value=True):coor.append(3)
        if st.checkbox("카카오 인증서",value=True):coor.append(4)
        if st.checkbox("KT지역화폐",value=True):coor.append(5)

        if st.button("전파"):
            if unfixed == "":
                st.error("공유될 원천사 정보 없음")
            else:
                clipboard.copy(f"{unfixed}")
                pd.DataFrame(coor).to_json(hotLineTriggerPath,orient='columns',force_ascii=False,indent=4)
                hotLine()
                with st.spinner('구동중입니다.'):
                    time.sleep(4)
                    st.success('핫라인을 확인해주세요.')

if __name__ == '__main__':
    H_page()