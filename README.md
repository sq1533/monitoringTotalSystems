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
--- mss&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(fast API 및 streamlit 웹 서버 / selenium 및 bs4 웹 이벤트 수집)
<br>
--- rm&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(selenium 및 bs4 웹 이벤트 수집)<br>
- __init()__.py
<br>
- loadPath.py&nbsp;&nbsp;&nbsp;(DB 상대경로 객체 생성)
<head>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
</head>
<div class="col-start-1 col-end-5 text-xl text-center grid grid-cols-7 items-center">
    <p class="col-start-1 col-end-8 font-bold text-left">구조</p>
    <div class="text-green-600"><i class="material-symbols-outlined"style="font-size:100px;">sdk</i></div>
    <div class="text-gray-700"><i class="material-symbols-outlined"style="font-size:50px;">label_important</i></div>
    <div class="text-indigo-900"><i class="material-symbols-outlined"style="font-size:100px;">select_window</i></div>
    <div class="text-blue-700"><i class="material-symbols-outlined"style="font-size:50px;">find_replace</i></div>
    <div class="text-indigo-900"><i class="material-symbols-outlined"style="font-size:100px;">problem</i></div>
    <div class="text-gray-700"><i class="material-symbols-outlined"style="font-size:50px;">label_important</i></div>
    <div class="text-red-500">
        <div><i class="material-symbols-outlined"style="font-size:50px;">http</i></div>
        <div><i class="material-symbols-outlined"style="font-size:100px;">browse</i></div>
    </div>
    <div class="text-xl">네이버 웍스</div>
    <div class="text-gray-700"><i class="material-symbols-outlined"style="font-size:50px;">label_important</i></div>
    <div class="text-xl">alarm.json</div>
    <div class="text-xl">MID 매칭</div>
    <div class="text-xl">MID_info.json</div>
    <div class="text-gray-700"><i class="material-symbols-outlined"style="font-size:50px;">label_important</i></div>
    <div class="text-xl">관제보조도구</div>
</div>
