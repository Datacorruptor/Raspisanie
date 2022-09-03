import streamlit as st
#st.set_page_config(layout="wide")
import requests
import xlrd
import datetime
import pandas as pd




dow = [
    'ПОНЕДЕЛЬНИК',
    'ВТОРНИК',
    'СРЕДА',
    'ЧЕТВЕРГ',
    'ПЯТНИЦА',
    'СУББОТА',
    'ВОСКРЕСЕНИЕ'
]

def get_rasp_file():
    proxies = {"http": "http://88.212.232.212:7497" }

    r = requests.get("https://www.mirea.ru/schedule/", proxies=proxies).content.decode(encoding="utf-8")
    course = 4
    r = r.split("Институт кибербезопасности и цифровых технологий")[1]

    untokenizedLinks = r.split("uk-link-toggle")
    tokenizedLinks = [""]*len(untokenizedLinks)
    for i in range(1,7):
        tokenizedLinks[i] = untokenizedLinks[i].split("href")[1].split('"')[1]

    url = tokenizedLinks[course]
    r = requests.get(url, proxies = {"http": "http://88.212.232.212:7497" }, allow_redirects=True)
    open('rasp.xls', 'wb').write(r.content)

def get_rasp_position():
    rb = xlrd.open_workbook('rasp.xls',formatting_info=True)

    for sheet in rb.sheets():
        for col_ind in range(sheet.ncols):
            col = sheet.col_values(col_ind)
            for i in range(4):
                if col[i].__contains__("БИСО-03-19"):
                    return sheet,col_ind

def get_rasp_data(sheet,col_ind):
    result = []
    header = sheet.col_values(0)
    time1 = sheet.col_values(2)
    time2 = sheet.col_values(3)
    parity = sheet.col_values(4)
    col = sheet.col_values(col_ind)
    type = sheet.col_values(col_ind+1)
    tutor = sheet.col_values(col_ind+2)
    cabinet = sheet.col_values(col_ind+3)
    hd=header[0]
    t1 = time1[0]
    t2 = time2[0]
    for i in range(len(col)):
        if len(header[i])>1 :
            hd = header[i]
        if len(time1[i])>1 :
            t1 = time1[i]
            t2 = time2[i]

        if str(hd).upper() in dow and len(parity[i])>0:
            result.append((hd,t1,t2,parity[i],col[i],type[i],tutor[i],cabinet[i]))

    return result

def get_current_rasp_data():

    get_rasp_file()
    sheet, col_ind = get_rasp_position()
    all_group_info = get_rasp_data(sheet, col_ind)

    current_date = datetime.date.today()
    current_dow = dow[current_date.weekday()]

    first_day = datetime.date(current_date.year,9,1)
    delta = current_date - first_day

    curr_week = (delta.days+first_day.weekday())//7+1
    curr_parity = curr_week%2


    res = []
    for info in all_group_info:
        if info[0] == current_dow and len(info[3])%2 == curr_parity:
            res.append(info)
    return res


# CSS to inject contained in a string
hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """



# Inject CSS with Markdown
st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

st.markdown(""" <style> 
    .font {font-size:10px;} 
</style> """, unsafe_allow_html=True)





info = get_current_rasp_data()

list = [[i[1],i[2],i[4].replace("\n"," / "),i[5].replace("\n"," / "),i[6].replace("\n"," / "),i[7].replace("\n"," / ")] for i in info]


timelist = [[int(i[2].split('-')[0]),int(i[2].split('-')[1]), "/".join([j for j in (i[7].replace("\n"," / ")+"/").split("/")[:-1] ]) ] for i in info if len(i[4])>1]

current_date = datetime.date.today()
current_dow = dow[current_date.weekday()]

first_day = datetime.date(current_date.year,9,1)
delta = current_date - first_day

curr_week = (delta.days+first_day.weekday())//7+1
curr_parity = curr_week%2

st.title("Сейчас идёт "+str(curr_week)+ " неделя")
st.header(str(current_dow))




df = pd.DataFrame(list, columns=['Начало',"Конец","Предмет","Вид","Препод","Кабинет"])
styler = df.style.hide_index()
st.write(styler.to_html()+"<br/>", unsafe_allow_html=True)

today = datetime.datetime.now()
start = today.replace(hour=0, minute=0, second=0, microsecond=0)
st.text("текущее время "+str(today.time()).split('.')[0])

nearest = '(нет пар)'
for t in timelist:
    if today.time() < datetime.time(hour = t[0],minute=t[1]):
        nearest = t[2]
        break
st.markdown("сейчас нужно идти в "+nearest)










