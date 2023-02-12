# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 01:15:17 2023

@author: tomas1608
"""

from selenium import webdriver
import time
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
s = Service("PATH") #Local path al chromedriver 

driver = webdriver.Chrome(service = s)

#Ir al URL
driver.get(url)
driver.maximize_window()

#La dejas pensar para que cargue
driver.implicitly_wait(10)

#Buscar el total de empleos mediante una busqueda por nombre de clase
y=driver.find_element(By.CLASS_NAME, 'results-context-header__job-count').text
y=pd.to_numeric(y)

#Mas o menos por loop traemos 25 trabajos aprox, necesitaremos 15 (+ o -)
i=1

while i <= ((y+100)/25):
    #Primero le decimos que scrolee de manera infinita
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);") #Le pedimos que baje hasta el final de la pagina
    time.sleep(3)
    i=i+1
    #Codigo para que toque el boton "Ver más empleos" cuando el mismo aparezca
    try:
        #Lo buscamos por XPATH
        send=driver.find_element(By.XPATH, "//button[@aria-label='Ver más empleos']")
        #Que lo ejecute
        driver.execute_script("arguments[0].click();", send)
        time.sleep(4)
        #En la pagina final, no encontrara boton
    except:
        pass
        time.sleep(4)
        
companyname=[]
jobtitle=[]
date=[]

#Para cada trabajo en los y trabajos
#Agarra el nombre de la compania, que lo identifica por su clase encontrada en el codigo fuente

#Antes, algunos filtros comunes para limpiar la data
filtros=["Electricistas", "Desarrollador", "Oficial y Medio Oficial (Zona Norte GBA)", "Plomero", "Oficial de Mantenimiento", 
        "Técnico de Gases Medicinales", "Scrum Master", "Ingeniero/a de Ascensores y Montacargas", "DevOps","Médicos", "Médico",
        "Arquitecto", "Developer", "Software", "software", "Traductor", "SAP", "Encargada/o de salón", "diagnóstico", "RPA"]
try:
    for i in range(y):
        #Busca por el nombre de clase, el trabajo/empresa que lo ofrece y obtiene el atributo text
        job=driver.find_elements(By.CLASS_NAME,'base-search-card__title')[i].text
        company=driver.find_elements(By.CLASS_NAME,'base-search-card__subtitle')[i].text
        #En el caso de la hora que se publica, se obtiene el atributo
        hora=driver.find_elements(By.CLASS_NAME, "job-search-card__listdate")[i].get_attribute("datetime")
        #Chequeo de que no tengan ninguna palabra de los filtros
        if all(x not in job for x in filtros):
            companyname.append(company)
            jobtitle.append(job)
            date.append(hora)
        else:
            continue
except IndexError:
    print("Done")

#Hacemos un df para cada una de las listas

companyfinal=pd.DataFrame(companyname, columns=["company"])
titlefinal=pd.DataFrame(jobtitle, columns=["Job"])

df=companyfinal.join(titlefinal)

df.to_csv("PATH")

# Para ver cual es la empresa que más demanda

subset=df.groupby(by="company").count()

subset=subset.sort_values("Job",ascending=False).head(15)

subset=subset.reset_index()

#Para facilitar la visualización de los charts y el mano de la data
for i in range(15):
    if subset["company"][i]=="Consejo Profesional de Ciencias Económicas de la Ciudad Autónoma de Buenos Aires":
        subset["company"][i]="Consejo de Ciencias Económicas CABA"
    else:
        continue
    
## Grafico de las empresas que más piden

#"indianred", "darksalmon", "lightcoral", navajowhite
colors=["darkred", "mediumvioletred","orchid", "sandybrown", "lightpink" , "khaki" , "orange", "gold", "lightseagreen", "mediumaquamarine", "lawngreen", "palegreen", "powderblue", "dimgray","lightgray"]

fig=go.Figure([go.Bar(x=subset["company"], y=subset["Job"], marker_color=colors)])

fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)",
                   "paper_bgcolor": "rgba(0, 0, 0, 0)",
})

fig.update_yaxes(showgrid=True, linecolor="#444", gridcolor="Lightgrey", title="Frecuencia",title_font_size=16)
fig.update_xaxes(showgrid=True, linecolor="#444", gridcolor="Lightgrey", title="Empresa", title_font_size=16)

fig.update_layout(font_family="Serif", font_size=13, title="<b>Ofertas laborales en LinkedIn por empleador</b><br>Para licenciados en Economia</br>")

fig.write_image("PATH/empleadores.jpeg")

##Gráfico seniority

#Buscamos las posibles categorías en los titulos de los trabajos

pasante=sum("pasante" in s.lower() for s in jobtitle)+sum("pasantía" in s.lower() for s in jobtitle)+sum("pasantia" in s.lower() for s in jobtitle)

junior=sum("jr" in s.lower() for s in jobtitle)+sum("junior" in s.lower() for s in jobtitle)

semi=sum("ssr" in s.lower() for s in jobtitle)+sum("semisenior" in s.lower() for s in jobtitle)

senior=(sum("sr" in s.lower() for s in jobtitle)-sum("ssr" in s.lower() for s in jobtitle))+sum("senior" in s.lower() for s in jobtitle)

level={"Pasante":pasante, "Junior":junior, "Semisenior": semi, "Senior": senior}

cat=list(level.keys())
freq=list(level.values())

color_2=["mediumaquamarine", "khaki", "lightpink", "orchid"]

fig=go.Figure([go.Bar(x=cat, y=freq, marker_color=color_2)])

fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)",
                   "paper_bgcolor": "rgba(0, 0, 0, 0)",
})

fig.update_yaxes(showgrid=True, linecolor="#444", gridcolor="Lightgrey", title="Frecuencia",title_font_size=20)
fig.update_xaxes(showgrid=True, linecolor="#444", gridcolor="Lightgrey", title="Experiencia", title_font_size=20)

fig.update_layout(font_family="Serif", font_size=15, title="<b>Ofertas laborales en LinkedIn por seniority</b><br>Para licenciados en Economia (solo se contabilizan los titulos de los empleos) </br>")

fig.write_image("PATH/seniority.jpeg")

#Nube de palabras

comment_words = ''
stopwords = set(STOPWORDS)

#Iterar por cada trabajo
for val in df["Job"]:
     
    val = str(val)
 
    # split el string del titulo del trabajo
    tokens = val.split()
     
    # Hacer miniscula cada palabra
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
     
    comment_words += " ".join(tokens)+" "
 
#Generar el objeto WordCloud en base al string comment_words y las stop
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

#Vamos a recolectar todos los links para poder entrar a cada uno, obtener la descripcion de cada puesto para ver cuales son las skills mas pedidas

lista2=[]

filtros2=["desarrollador","scrum","medico", "developer","arquitecto", "electricistas", "oficial-y-medio-oficial", "ecografista",
       "plomero", "oficial-de-mantenimiento", "guardia", "software", "gases-medicinales", "traductor", "sap-hr", "cadena-internacional-de-bares","ingeniero-a-de-ascensores", "devops","médicos", "médico"]

#No se bien por que algunas ofertas no pertenecen a la clase base card full link, por lo que no me las trae cuando traigo todos los elementos
#La diferencia es que algunos tienen el /div/ y otros no, por eso mejor buscar por XPATH

for i in range(1,y+1):
    #Ponemos un try porque si le metemos un Xpath con div a un elemento que no tiene div en el path, se rompe
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
            #Aquellos que no tienen el div, queda asi el XPATH
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
        #Cliquear el "Ver mas" de cada descripcion
        driver.find_element(By.XPATH,"//*[@id='main-content']/section[1]/div/div/section[1]/div/div/section/button[1]").click()
        time.sleep(3)
        #Obtener el texto de la descripcion
        a=driver.find_element(By.CLASS_NAME,"description__text").text
        lista.append(a)
        time.sleep(3)
    except:
        continue


#Cuenta todas las palabras relevantes

sql=sum('sql' in s.lower() for s in lista)
excel=sum('excel' in s.lower() for s in lista)
python=sum('python' in s.lower() for s in lista) +sum('phyton' in s.lower() for s in lista) #Varias ofertas piden phyton en vez de python
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

fig=go.Figure([go.Bar(x=data1["Skill"], y=data1["Count"],marker_color=colores)])

fig.update_layout({"plot_bgcolor": "rgba(0, 0, 0, 0)",
                   "paper_bgcolor": "rgba(0, 0, 0, 0)",
})

fig.update_yaxes(showgrid=True, gridcolor="#eee", linecolor="#444", title="Frecuencia",title_font_size=20)

fig.update_xaxes(showgrid=True, gridcolor="#eee", linecolor="#444", title="Programa",title_font_size=20)

fig.update_layout(title="<b>Skills más requeridas para Lic. en Economía</b><br>En LinkedIn</br>", font_family="Serif", font_size=15)

fig.write_image("PATH/skills.jpeg")
