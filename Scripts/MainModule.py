###################################################################
#Elaborado por: Carlos Varela y Joseph Tenorio
#Fecha de creación: 28/04/2019
#Fecha de última de modificación: 13/05/2019
#Versión: 3.7.3
###################################################################

#Importacón de librerías
import xml.etree.ElementTree as ET
import requests
from xml.dom import minidom
import codecs
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase 
from email import encoders
import http.client as httplib
import datetime
from requests.exceptions import HTTPError
import re
import os
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename


#Definición de funciones
def obtenerFrase ():
    """
    Funcionamiento: Llama a la verificación de conexión a internet y realiza la llamada a la API
    Entradas: N/A
    Salidas: Un booleano equivalente a False en caso de error, o la variable respuesta (dict) si el proceso fue exitoso 
    """
    while True:
        if revisarInternet()==True:
            break
        else:
            msg=messagebox.showinfo("Error","No hay conexión a internet")
            return False
    respuesta=requests.get("http://swquotesapi.digitaljedi.dk/api/SWQuote/RandomStarWarsQuote")
    try:
        respuesta.raise_for_status()
        respuesta=respuesta.text
        respuesta=dict(eval(respuesta))   
        return respuesta
    except HTTPError as http_err:
        msg1=messagebox.showinfo("Error","La API no ha respondido, puede deberse a que esta se encuentra caida o bloqueada.")
        return False

def montarEnDicccionario(DiccionarioPersonajes,contP,cita):
    """
    Funcionamiento: Inserta en el diccionario global la información de la cita obtenida
    Entradas: DiccionarioPersonajes (dict), contP (int), cita(list)
    Salidas: Una lista que incluye a DiccionarioPersonajes (dict) y contP (int)
    """
    personaje=cita[1]
    if personaje not in DiccionarioPersonajes.keys():
        contP+=1
        letraF=(personaje[len(personaje)-1]).upper()
        DiccionarioPersonajes[personaje]=[("#"+personaje[0]+str("%03d"%contP)+"-"+letraF),1]
    else:
        lista=DiccionarioPersonajes[personaje]
        ant=lista[1]
        lista[1]=ant+1
        DiccionarioPersonajes[personaje]=lista
    return [DiccionarioPersonajes,contP]

def montarEnMatriz (matrizFrases,cita,DiccionarioPersonajes,contP):
    """
    Funcionamiento: Inserta en la matriz global la información de la cita obtenida
    Entradas: matrizFrases (list), cita (str), DiccionarioPersonajes (dict), contP (int)
    Salidas: Una lista que contiene a matrizFrases(list) y los datos del personaje
    """
    if cita == False:
        return
    diccionario=montarEnDicccionario(DiccionarioPersonajes,contP,cita)
    for i in range(len(matrizFrases)):
        fila=matrizFrases[i]
        if cita[1]==fila[0]:
            if cita[0] not in fila[1]:
                (matrizFrases[i])[1].append(cita[0])
                (matrizFrases[i])[2].append(cita[2])
                return [matrizFrases,diccionario[0],diccionario[1]]
            else:
                return [matrizFrases,diccionario[0],diccionario[1],True]
    nuevaFila=[cita[1],[cita[0]],[cita[2]],(diccionario[0])[cita[1]][0]]
    matrizFrases.append(nuevaFila)
    return [matrizFrases,diccionario[0],diccionario[1]]
    
def determinarCita ():
    """
    Funcionamiento: Realiza la llamada a la API y organiza la variable "cita", usada por otras funciones
    Entradas: N/A
    Salidas: Un booleano equivalente a False si la llamada falló, o la cita (list) solicitada
    """
    diccionario = obtenerFrase()
    if diccionario == False:
        return False
    cita = diccionario["starWarsQuote"]
    if diccionario["id"]==15:
        cita=cita.split (". — ")
        cita.append(diccionario["id"])
        return cita
    cita = cita.split(" — ")
    if len (cita)==1:
        cita=cita[0].split (" ? ")
        if len (cita)==1:
            cita=cita[0].split (" - ")
            if len (cita)==1:
                cita=cita[0].split (" _ ")
    cita[1]=re.sub(r' \([^)]*\)','', cita[1])
    cita.append(diccionario["id"])
    return cita

def crearXML(matrizFrases,DiccionarioPersonajes,contP):
    """
    Funcionamiento:Crea el xml a partir de los datos del programa
    Entradas: matrizFrases,DiccionarioPersonajes,contP
    Salidas:XML
    """
    root=ET.Element("Backup")
    matriz=ET.SubElement(root,"Matriz")
    for lista in matrizFrases:
        personaje=ET.SubElement(matriz,"Personaje",)
        name=ET.SubElement(personaje,"Name",infoP=lista[0],Code=lista[3])
        for frase in lista[1]:
            phrase = ET.SubElement(personaje, "Phrases",frases=frase)
        for id in lista[2]:
            ID= ET.SubElement(personaje,"ID",ID=str(id))
    Diccionario=ET.SubElement(root,"Diccionario")
    for key in DiccionarioPersonajes:
        personaje = ET.SubElement(Diccionario, "Personaje")
        for i in range(1):
            codigoP=ET.SubElement(personaje,"App_Code",Key=key,Code=DiccionarioPersonajes[key][i])
            llamadaAPI=ET.SubElement(personaje,"Llamadas",Llamadas=str(DiccionarioPersonajes[key][i+1]))
    variables=ET.SubElement(root,"Variables",contador=str(contP))
    xml=(prettify(root))
    with open('Backup.xml', "w",encoding='UTF-8') as file:
        file.write(xml)
    return

def cargarBackup(matrizFrases,DiccionarioPersonajes):
    """
    Funcionamiento:Carga la matriz y diccionario a partir de un xml
    Entradas:matrizFrases,DiccionarioPersonajes
    Salidas:matrizFrases,DiccionarioPersonajes aunque no aparezca
    """
    with codecs.open('Backup.xml', 'r', encoding='UTF-8') as xml:
        tree = ET.parse(xml)
    root = tree.getroot()
    for personaje in root.iter("Personaje"):
        for name in personaje.iter("Name"):
            lista=[]
            listaFrases = []
            listaID=[]
            lista.append(name.attrib.get("infoP"))
            for frase in personaje.iter("Phrases"):
                frase = frase.attrib.get("frases")
                listaFrases.append(frase)
            lista.append(listaFrases)
            for id in personaje.iter("ID"):
                ids= id.attrib.get("ID")
                listaID.append(int(ids))
            lista.append(listaID)
            lista.append(name.attrib.get("Code"))
            matrizFrases.append(lista)
    for diccionario in root.iter("Diccionario"):
        for personaje in diccionario:
            for info in personaje.findall("App_Code"):
                name=info.attrib.get("Key")
                code=info.attrib.get("Code")
            for contador in personaje.findall("Llamadas"):
                peticiones = int(contador.attrib.get("Llamadas"))
            DiccionarioPersonajes[name]= [code,peticiones]
    return

def cargarContador():
    """
    Funcionamiento:carga el contador global usado en la creación de códigos de personaje
    Entradas:NA
    Salidas:ContP1
    """
    with codecs.open('Backup.xml', 'r', encoding='latin-1') as xml:
        tree = ET.parse(xml)
    root = tree.getroot()
    for contador in root.iter("Variables"):
        contP1=int(contador.attrib.get("contador"))
    return contP1


def prettify(elem):
    """
    Funcionamiento:Ordena el xml de forma más legible
    Entradas:elem
    Salidas:elem reparseado de manera legible
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
    
def shareBackup(lista):
    """
    Funcionamiento:Crea el xml para el share
    Entradas:lista(de frases seleccionadas por el usuario)
    Salidas:archivo(xml)
    """
    fecha = str(datetime.datetime.now())
    fecha = fecha[0:19].replace(":", "-").replace(" ", "-")
    root=ET.Element("Share")
    for frase in lista:
        ET.SubElement(root,"Frase",Phrase=frase)
    archivo="share-"+fecha+".xml"
    xml = (prettify(root))
    with open(archivo, "w") as file:
        file.write(xml)
    file.close()
    return archivo

def cargarShareXML(archivo):
    """
    Funcionamiento:carga el xml del share
    Entradas:archivo(xml)
    Salidas:listaFra(lista de frases del xml)
    """
    listaFra=[]
    with codecs.open(archivo, 'r', encoding='latin-1') as xml:
        tree = ET.parse(xml)
    root = tree.getroot()
    for frase in root.iter("Frase"):
        frase = frase.attrib.get("Phrase")
        frase = frase.replace("", "’")
        listaFra.append(frase)
    return listaFra
        

def definirMayor (DiccionarioPersonajes):
    """
    Funcionamiento: Determina el personaje con mayor cantidad de frases recibidas desde la API
    Entradas: DiccionarioPersonajes (dict)
    Salidas: Un string indicando si no se han solicitado frases o el personaje con más resultados
    """
    mayor=0
    resul=""
    for key in DiccionarioPersonajes:
        if DiccionarioPersonajes[key][1]>mayor:
            mayor=DiccionarioPersonajes[key][1]
            resul=key
        elif DiccionarioPersonajes[key][1]==mayor:
            resul=resul+", "+key
    if mayor==0:
        return "No se han solicitado frases aún"
    else:
        return "El o los personajes con más resultados: "+resul

def enviarCorreo (matrizFrases,destinatario):
    """
    Funcionamiento: Envía un correo con al destinatario indicado, el cual incluye la lista de frases indicada
    Entradas: matrizFrases (list), destinatario (str)
    Salidas: Un booleano equivalente a True si el proceso fue exitoso, N/A en caso contrario
    """
    while True:                                 #Verificación de conexión a internet
        if revisarInternet()==True:
            break
        else:
            msg=messagebox.showinfo("Error","No hay conexión a internet")
            return
    nombre = shareBackup(matrizFrases)          #Llamada a shareBackup
    context = ssl.create_default_context()      
    while True:                                 #Verificación de destinatario válido                
        if destinatario==None or destinatario=="":
            msg=messagebox.showinfo("Error","Favor ingresar un correo de destino")
            os.remove(nombre)
            return
        elif re.match(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?",destinatario):
            break
        else:
            msg=messagebox.showinfo("Error","El correo ingresado no tiene el formato de una dirección válida")
            os.remove(nombre)
            return
    msg = MIMEMultipart()                       #Creación de elemento "mensaje"
    msg['From'] = "lagalleradepython@gmail.com"
    msg['To'] = destinatario
    msg['Subject'] = "Citas de StarWars"
    mensaje = "Alguien desea compartir las siguientes citas de StarWars contigo"
    msg.attach(MIMEText(mensaje, 'plain'))      #Se une la variable mensaje al objeto antes creado
    filename = nombre                           
    attachment = open(nombre, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    text = msg.as_string()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server: #Conexión con el servidor de gmail
        try:
            server.login("lagalleradepython@gmail.com", "Joseph20*")        
            server.sendmail("lagalleradepython@gmail.com",destinatario,text)
        except UnicodeEncodeError:                                          #Validación de error por carácteres inválidos
            msg=messagebox.showinfo("Error","El correo ingresado contiene carácteres no válidos")
            attachment.close()
            os.remove(nombre) 
            return 
    msg=messagebox.showinfo("Envío de frases","Correo enviado")
    attachment.close()                      #Cierre del xml creado
    os.remove(nombre)                       #Eliminación del xml creado
    return True


def revisarInternet():
    """
    Funcionamiento: Verifica la conexión a internet del dispositivo
    Entradas: N/A
    Salidas: Un valor booleano, True si se verifica la conexión y False en cualquier otro caso
    """
    conn = httplib.HTTPConnection("www.google.com", timeout=4)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

def nuevaFrase (matrizFrases,DiccionarioPersonajes,contP):
    """
    Funcionamiento: Función encargada de coordinar las funciones que llaman a la API y organizan el resultado
    Entradas: matrizFrases (list), DiccionarioPersonajes (dict), contP (int)
    Salidas: Una tupla en caso de frase repetida, una lista en caso de error en la llamada, y un entero si el proceso fue exitoso
    """
    cita=determinarCita()
    if cita!=False:
        Provisional=montarEnMatriz (matrizFrases,cita,DiccionarioPersonajes,contP)
        contP=Provisional[2]
        DiccionarioPersonajes=Provisional[1]
        matrizFrases=Provisional[0]
        if len(Provisional)==4:
            return contP,"repetir"
        else:
            return contP
    else:
        return [contP,False]





