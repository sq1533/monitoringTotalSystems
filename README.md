# Monitoring Tatal Systems 구성과 주요 기능
***
## 1. 구성
<br>
MonitoringTatalSystems
<br>
--- DB&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(gitingnore / json, HTML)
<br>
--- faxChecker&nbsp;(streamlit 웹서버 / selenium 및 bs4 웹 이벤트 수집)
<br>
--- <mark style="background-color: #FF0000;">mss</mark>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(fast API 및 streamlit 웹 서버 / selenium 및 bs4 웹 이벤트 수집)
<br>
--- rm&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(selenium 및 bs4 웹 이벤트 수집)<br>
- __init()__.py
<br>
- loadPath.py&nbsp;&nbsp;&nbsp;(DB 상대경로 객체 생성)
<br><br>

## 2. mss 구동방식
<br>

![MSS 시스템 구동](https://github.com/sq1533/monitoringTotalSystems/blob/main/image.png)
