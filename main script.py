# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 01:15:17 2023

@author: tomas1608
"""

from selenium import webdriver
import time
import datetime as dt
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from wordcloud import WordCloud, STOPWORDS


url = "https://ar.linkedin.com/jobs/search?keywords=Economia&location=Argentina&locationId=&geoId=100446943&f_TPR=&f_PP=103813819&position=1&pageNum=0"

#Abre Chrome
s = Service("PATH al chromedriver.exe")
driver = webdriver.Chrome(service = s)

#Ir al URL
driver.get(url)
driver.maximize_window()

#La dejas pensar para que cargue todo
driver.implicitly_wait(10)

#Esto nos permite encontrar elementos de la web por el tipo de clase
#Nos va a dar el total de empleos
y=driver.find_element(By.CLASS_NAME, 'results-context-header__job-count').text

y=pd.to_numeric(y) #Hacerlo un int

#Mas o menos por loop traemos 25 trabajos aprox, necesitaremos 15 (+ o -)

i=1

while i <= ((y+100)/25):
    #Primero le decimos que scrolee de manera infinita
    #El modulo execute script le dice que ejecute lo que sigue entre comillas
    #Que basicamente le pide desde el inicio de la pagina hasta lo max que se pueda
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    time.sleep(3)
    i=i+1
    #Debemos ahora configurar que se ejecute el botón "Ver mas trabajos" una vez llegue al final de la hoja
    try:
        send=driver.find_element(By.XPATH, "//button[@aria-label='Ver más empleos']")
        driver.execute_script("arguments[0].click();", send)
        time.sleep(4)
        
        #En la página final, no estará ese botón
    except:
        pass
        time.sleep(4)
        
companyname=[]
jobtitle=[]
horario=[]

#Para cada trabajo en los y trabajos
#Agarra el nombre de la compania, que lo identifica por su clase encontrada en el codigo fuente

filtros=["Electricistas", "Desarrollador", "Oficial y Medio Oficial (Zona Norte GBA)", "Plomero", "Oficial de Mantenimiento", 
        "Técnico de Gases Medicinales", "Scrum Master", "Ingeniero/a de Ascensores y Montacargas", "DevOps","Médicos", "Médico",
        "Arquitecto", "Developer", "Software", "software", "Traductor", "SAP", "Encargada/o de salón", "diagnóstico", "RPA"]
try:
    for i in range(y):
        job=driver.find_elements(By.CLASS_NAME,'base-search-card__title')[i].text
        company=driver.find_elements(By.CLASS_NAME,'base-search-card__subtitle')[i].text
        hora=driver.find_elements(By.CLASS_NAME, "job-search-card__listdate")[i].get_attribute("datetime")
        if all(x not in job for x in filtros):
            companyname.append(company)
            jobtitle.append(job)
            horario.append(hora)
        else:
            continue

except IndexError:
    print("Done")

#Hacemos un df para cada una de las listas

companyfinal=pd.DataFrame(companyname, columns=["company"])
titlefinal=pd.DataFrame(jobtitle, columns=["Job"])

df=companyfinal.join(titlefinal)

#Tener la fecha como "XX of month" para titulo de graficos y de csv

hoy=dt.datetime.now()

fecha=str(hoy.day)+" of "+ hoy.strftime("%B")

#Guardar df

df.to_csv("PATH/Ofertas laborales al {}".format(fecha))

# Para ver cual es la empresa que más demanda

subset=df.groupby(by="company").count()

subset=subset.sort_values("Job",ascending=False).head(15)

subset=subset.reset_index()

#Cambio de nombre para mejorar la visualización
for i in range(15):
    if subset["company"][i]=="Consejo Profesional de Ciencias Económicas de la Ciudad Autónoma de Buenos Aires":
        subset["company"][i]="Consejo de Ciencias Económicas CABA"
    else:
        continue
    
## Grafico de las empresas que más demandan empleo


#"indianred", "darksalmon", "lightcoral", navajowhite
colors=["darkred", "mediumvioletred","orchid", "sandybrown", "lightpink" , "khaki" , "orange", "gold", "lightseagreen", "mediumaquamarine", "lawngreen", "palegreen", "powderblue", "dimgray","lightgray"]

fig=go.Figure([go.Bar(x=subset["company"], y=subset["Job"], marker_color=colors)])

fig.update_layout(plot_bgcolor = "white")

fig.update_yaxes(showgrid=True, linecolor="#444", gridcolor="Lightgrey", title="Frequency",title_font_size=16)
fig.update_xaxes(showgrid=True, linecolor="#444", gridcolor="Lightgrey", title="Company", title_font_size=16)

fig.update_layout(font_family="Serif", font_size=13, title="<b> Companies by amount of job offers for Economists in Linkedin </b><br>Updated to {}<br></br>".format(fecha))

fig.write_image("PATH/empleadores.jpeg")

print("Chart de empleadores hecho")

##Gráfico seniority

pasante=sum("pasante" in s.lower() for s in jobtitle)+sum("pasantía" in s.lower() for s in jobtitle)+sum("pasantia" in s.lower() for s in jobtitle)

junior=sum("jr" in s.lower() for s in jobtitle)

semi=sum("ssr" in s.lower() for s in jobtitle)

senior=sum("sr" in s.lower() for s in jobtitle)-sum("ssr" in s.lower() for s in jobtitle)


level={"Pasante":pasante, "Junior":junior, "Semisenior": semi, "Senior": senior}

cat=list(level.keys())
freq=list(level.values())

colort=["mediumaquamarine", "khaki", "lightpink", "orchid"]

fig=go.Figure([go.Bar(x=cat, y=freq, marker_color=colort)])

fig.update_layout(plot_bgcolor = "white")

fig.update_yaxes(showgrid=True, linecolor="#444", gridcolor="Lightgrey", title="Frequency",title_font_size=20)
fig.update_xaxes(showgrid=True, linecolor="#444", gridcolor="Lightgrey", title="Seniority", title_font_size=20)

fig.update_layout(font_family="Serif", font_size=15, title="<b>Job offers for Economists in LinkedIn by seniority</b><br>Updated to {}</br>".format(fecha)) 

fig.write_image("PATH/seniority.jpeg")

print("Gráfico de seniority hecho")
#Nube de palabras

comment_words = ''
stopwords = set(STOPWORDS)

for val in df["Job"]:
     
    val = str(val)
 
    # split the value
    tokens = val.split()
     
    # Converts each token into lowercase
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
     
    comment_words += " ".join(tokens)+" "
 

wc = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(comment_words)
 
# plot the WordCloud image                      
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wc)
plt.axis("off")
plt.tight_layout(pad = 0)
 
plt.savefig("PATH/nube.jpeg")

print("Gráfico de Nube hecho")

#Get the href

lista2=[]

filtros2=["desarrollador","scrum","medico", "developer","arquitecto", "electricistas", "oficial-y-medio-oficial", "ecografista",
       "plomero", "oficial-de-mantenimiento", "guardia", "software", "gases-medicinales", "traductor", "sap-hr", "cadena-internacional-de-bares","ingeniero-a-de-ascensores", "devops","médicos", "médico"]
#Algunas ofertas no pertenecen a la clase base card full link, por lo que no las trae cuando traigo todos los elementos by CLASS.NAME

#La diferencia es que algunos tienen el /div/ y otros no

#Entonces, vamos a buscarlos por Xpath
for i in range(1,y+1):
    #Ponemos un try porque si encuentra un elemento cuyo Xpath no tiene "div" no traeria su url
        try:
            #Aquellos que aparece el div, el Xpath queda asi
            a=driver.find_elements(By.XPATH, "//*[@id='main-content']/section[2]/ul/li[{}]/div/a".format(i))
            link=a[0].get_attribute("href")
            if all(x not in link for x in filtros2):
                lista2.append(link)
                print(i)
            else:
                continue
        except Exception as e:
            #Pasamos como excepcion a aquellos que no tienen el "div"
            a=driver.find_elements(By.XPATH, "//*[@id='main-content']/section[2]/ul/li[{}]/a".format(i))
            link=a[0].get_attribute("href")
            if all(x not in link for x in filtros2):
                lista2.append(link)
                print(i)
            else:
                continue

#Scrapear las skills mas pedidas

lista=[]

for i in range(len(lista2)+10):
    try:
        driver.get(lista2[i])
        time.sleep(3)
        driver.find_element(By.XPATH,"//*[@id='main-content']/section[1]/div/div/section[1]/div/div/section/button[1]").click()
        time.sleep(3)
        a=driver.find_element(By.CLASS_NAME,"description__text").text
        lista.append(a)
        time.sleep(3)
    except:
        continue


#Cuenta todas las palabras relevantes

sql=sum('sql' in s.lower() for s in lista)
excel=sum('excel' in s.lower() for s in lista)
python=sum('python' in s.lower() for s in lista) +sum('phyton' in s.lower() for s in lista) #Typo bastante comun
tableau=sum('tableau' in s.lower() for s in lista)
word=sum('office' in s.lower() for s in lista)
power=sum("power bi" in s.lower() for s in lista) + sum("powerbi" in s.lower() for s in lista)
r=sum('en R' in s for s in lista)+sum('EN R' in s for s in lista)+sum('En R' in s for s in lista)
sap=sum('sap' in s.lower() for s in lista)

data={"SQL": sql, "Excel": excel, "Python": python, "Tableau": tableau, "Office": word, "Power BI": power, "R": r, "SAP": sap}

courses = list(data.keys())
values = list(data.values())

data1=pd.DataFrame(data.items(), columns=["Skill", "Count"])

colores=["slateblue", "seagreen", "orchid", "yellow", "mediumspringgreen", "orange", "crimson", "powderblue", "peru", "crimson"]

#Grafico skills mas demandadas

fig=go.Figure([go.Bar(x=data1["Skill"], y=data1["Count"],marker_color=colores)])

fig.update_layout(plot_bgcolor = "white")

fig.update_yaxes(showgrid=True, gridcolor="#eee", linecolor="#444", title="Frequency",title_font_size=20)

fig.update_xaxes(showgrid=True, gridcolor="#eee", linecolor="#444", title="Skills",title_font_size=20)

fig.update_layout(title="<b>Most demanded skills for economists in LinkedIn</b><br>Updated to {}</br>".format(fecha), font_family="Serif", font_size=15)

fig.write_image("PATH/skills.jpeg")

print("Gráfico de skills hecho")
