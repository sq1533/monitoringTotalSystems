import json
import pandas as pd
import requests
import streamlit as st

from monitoringTotalSystems.loadPath import midInfoPath

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

#판다스 DataFrame으로 호출
midInfo = pd.read_json(midInfoPath,orient="records",dtype={"mid":str,"info":str})
midList = midInfo['mid'].tolist()

#데이터 생성 및 수정 fast API
url = "http://127.0.0.1:8501/mk_info"
def create():
    requests.post(url,json.dumps(mk_info))

def change():
    requests.put(url,json.dumps(mk_ch))

#데이터 삭제 fast API
url_d = "http://127.0.0.1:8501/mk_info_d"
def delete():
    requests.post(url_d,json.dumps(mk_d))

#생성/수정/삭제 구분 tabs설정
tab1,tab2,tab3 = st.tabs(["생성","수정","삭제"])

#생성
with tab1:
    with st.form(key="mk_info"):
        mid: str = st.text_input("mid", max_chars=20)
        info: str = st.text_area("정보")
        mk_info = {
            "mid":mid,
            "info":info.replace('\n','<br>')
        }
        btn_1 = st.form_submit_button(label="생성")
        if btn_1:
            if mk_info['mid'] not in midList:
                create()
                st.markdown("생성완료")
            else:
                st.markdown("MID가 이미 존재합니다.")

#수정
with tab2:
    mid: str = st.text_input("mid", max_chars=20)
    btn_2 = st.button(label="조회")
    if btn_2:
        if mid not in midList:
            st.markdown("MID가 존재하지 않습니다.")
    with st.form(key="mk_ch"):
        if mid not in midList:
            swap = "수정 전 mid를 조회 해주세요"
        else:
            swap = mid
        mid: str = st.text_input("mid",swap,max_chars=20)
        info: str = st.text_area("정보",midInfo.loc[midInfo['mid']==swap]['info'].tolist()[0].replace("<br>","\n"),height=250)
        mk_ch = {
            "mid":mid,
            "info":info.replace('\n','<br>')
        }
        btn_3 = st.form_submit_button(label="수정")
        if btn_3:
            change()
            st.markdown("수정완료")

#삭제
with tab3:
    with st.form(key="mk_d"):
        mid: str = st.text_input("mid", max_chars=20)
        mk_d = {
            "mid":mid
        }
        btn_4 = st.form_submit_button(label="삭제")
        if btn_4:
            if mk_d['mid'] not in midList:
                st.markdown("MID가 존재하지 않습니다.")
            else:
                delete()
                st.markdown("삭제완료")