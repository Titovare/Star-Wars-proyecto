#Importacón de librerías
import xml.etree.ElementTree as ET
import requests
from xml.dom import minidom
import re


#Variables Globales
matrizFrases = []
DiccionarioPersonajes = {}
contP=0

#Definición de funciones

def obtenerFrase ():
    respuesta=(requests.get("http://swquotesapi.digitaljedi.dk/api/SWQuote/RandomStarWarsQuote")).text
    respuesta=dict (eval(respuesta))
    print (respuesta)
    return respuesta

def montarEnDicccionario(cita):
    global contP
    global DiccionarioPersonajes
    personaje=cita[1]
    if personaje not in DiccionarioPersonajes.keys():
        global contP
        contP+=1
        letraF=(personaje[len(personaje)-1]).upper()
        DiccionarioPersonajes[personaje]=[("#"+personaje[0]+str("%03d"%contP)+"-"+letraF),1]
    else:
        lista=DiccionarioPersonajes[personaje]
        ant=lista[1]
        lista[1]=ant+1
        DiccionarioPersonajes[personaje]=lista
    return DiccionarioPersonajes

def montarEnMatriz ():
    global matrizFrases
    cita=determinarCita()
    diccionario=montarEnDicccionario(cita)
    for i in range(len(matrizFrases)):
        fila=matrizFrases[i]
        if cita[1]==fila[0]:
            if cita[0] not in fila[1]:
                (matrizFrases[i])[1].append(cita[0])
                (matrizFrases[i])[2].append(cita[2])
                return
            else:
                return
    nuevaFila=[cita[1],[cita[0]],[cita[2]],diccionario[cita[1]][0]]
    matrizFrases.append(nuevaFila)
    return
    
def determinarCita ():
    diccionario = obtenerFrase()
    cita = diccionario["starWarsQuote"]
    cita = cita.split(" — ")
    if len (cita)==1:
        cita=cita[0].split (" ? ")
        if len (cita)==1:
            cita=cita[0].split (" - ")
    cita.append(diccionario["id"])
    return cita
def crearXML():
    global matrizFrases
    global DiccionarioPersonajes
    root=ET.Element("Backup")
    matriz=ET.SubElement(root,"Matriz")
    for lista in matrizFrases:
        if re.search(" ",lista[0]):
            nombre=lista[0].replace(" ","_")
        else:
            nombre=lista[0]
        personaje=ET.SubElement(matriz,nombre,)
        name=ET.SubElement(personaje,"Name",infoP=lista[0])
        for frase in lista[1]:
            phrase = ET.SubElement(personaje, "Phrases",frases=frase)
        for ide in lista[2]:
            ID = ET.SubElement(personaje,"IDs",ID=str(ide))
        Code = ET.SubElement(personaje,"Code",Code=str(lista[3]))
    Diccionario=ET.SubElement(root,"Diccionario")
    for key in DiccionarioPersonajes:
        llave=str(key).replace(" ","_")
        personaje=ET.SubElement(Diccionario,llave)
        for i in range(1):
            codigoP=ET.SubElement(personaje,"App_Code",Code=DiccionarioPersonajes[key][i])
            llamadaAPI=ET.SubElement(personaje,"Cantidad_de_llamadas_a_la_API",Llamadas=str(DiccionarioPersonajes[key][i+1]))
    tree=ET.ElementTree(root)
    ET.dump(root)
    xml=(prettify(root))
    with open('Backup.xml', "w") as file:
        file.write(xml)

    return
def prettify(elem):
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")






#PP
while True:
    opcion = int(input ("Que quiere hacer?: "))
    if opcion==1:
       montarEnMatriz()
    else:
        print (matrizFrases)
        print (DiccionarioPersonajes)
        break
crearXML()


