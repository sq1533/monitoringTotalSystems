import os
import pandas
import streamlit as st

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

#AI_MON simple 알람 타켓
nonePay = [':거래없음',':거래감소',':거래(성공건)없음']
successDown = [':성공율 하락',':비정상환불',':비정상취소']
error = [':동일오류',':오류발생']
upperPay = [':거래급증',':거래(오류)급증']
all = nonePay + successDown + error + upperPay

categorys = {"전체":all,"성공률하락":successDown,"거래감소":nonePay,"Error":error,"거래급증":upperPay}

cols1,cols2,cols3,cols4 = st.columns(spec=4,gap='small',vertical_alignment="center")

startDate = cols1.date_input(label="조회 범위(시작)",format="YYYY-MM-DD")
endDate = cols2.date_input(label="조회 범위(종료)",format="YYYY-MM-DD")
index = cols3.selectbox(label="카테고리",options=categorys.keys())
text = cols4.text_input(label="포함된 단어")

lookupButton = st.button(label="조회")
if lookupButton:
    blank = pandas.DataFrame(data={"Alarm":[],"date":[],"check":[]})
    dateRange = pandas.date_range(start=startDate,end=endDate)
    dateList = [[date.strftime("%y%m%d"),date.strftime("%m/%d")] for date in dateRange]

    for jsonFile in dateList:
        AlarmPath = os.path.join(os.path.dirname(__file__),"..","..","DB","Alarm",f"worksAlarm_{jsonFile[0]}.json")

        if os.path.exists(AlarmPath):
            Data = pandas.read_json(AlarmPath,orient="records",dtype={"Alarm":str,"date":str,"check":str})
            Data = Data[Data["date"].str.contains(jsonFile[1])]
            blank = pandas.concat(objs=[blank,Data],ignore_index=True)
        else:
            st.error(f"{jsonFile} 알람 파일은 없습니다.")
            break

    categorysFilter = blank[blank["Alarm"].str.contains("|".join(categorys[index]))]

    if text:
        textFilter = categorysFilter[categorysFilter["Alarm"].str.contains(text)]
        textFilter["Alarm"] = textFilter["Alarm"].str.replace("<br>","",regex=True)
        result = textFilter.sort_values(by="date")
        st.write(result)

    else:
        categorysFilter["Alarm"] = categorysFilter["Alarm"].str.replace("<br>","",regex=True)
        result = categorysFilter.sort_values(by="date")
        st.write(result)