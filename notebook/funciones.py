import re # utilizar expresiones regulares
import pandas as pd
import json
import xmltodict #para convertir archivos xml a diccionarios

# Extraer y transformar datos del archivo DICCIONARIO_REACCIONES_ADVERSAS.xml

def abrir_xml(filepath):

    """
    Para abrir un archivo xml, indicándole desde que ruta lo queremos

    Args:
        filepath: ruta del archivo que queremos abrir y leer

    Returns:
        El archivo xml leido en python
    """
    fichero = open(filepath,"r", encoding="utf8") # esto es otro error que tuve que mirar en internet para que funcionase
    xml_data= fichero.read().replace("&#x2;", ' ') # me daba error una linea, y los caracteres que me aparecieron en el error los coloque y funciono
    data =xmltodict.parse(xml_data)
    return data


def obtener_reaccion(id: str, reaccionesAdversas: dict):  
    """
    Para obtener las reacciones adversas por medicamento, reemplazando el número id por su valor en string

    Args:
        id: número id ['id_signo'] de la reacción de la cual queremos obtener su valor string ['ds_signo']
        reaccionesAdversas: diccionario necesario para poder filtrar, en este caso nos metemos 2 capas hacia dentro -> ['aemps_prescripcion_reacciones_adversas']['reacciones_adversas']

    Returns:
        Valor string correspondiente al id de las reacciones adversas de un medicamento
    """
    nombre = ''
    for e in reaccionesAdversas['aemps_prescripcion_reacciones_adversas']['reacciones_adversas']:
        if e['id_signo'] == id:
            nombre = e['ds_signo']
    return nombre

# Extraer y transformar datos del archivo PrescripciónVET.xml 

def get_prescripcions_esp(bloquePrescripcion: list, especies: list): 
    """
    Para obtener una lista de diccionarios de medicamentos filtrado por especies.

    Args:
        bloquePrescripcion: el filtro de keys necesario para llegar a la info que quiero
        especies: las especies que quiera seleccionar

    Returns:
        Una lista de diccionarios filtrado por especie 
    """
    prescripciones = []
    for prescripcionDict in bloquePrescripcion:
        if not 'dosisrecomendadaespecie' in prescripcionDict:
            continue
        for dosisEspecieDict in prescripcionDict['dosisrecomendadaespecie']: # casi todos los valores eran dict, pero hay algunos str, en este caso los ignoramos y seguimos mirando lso demás
            if type(dosisEspecieDict) == str: # esto daba un error si no se especificaba que fuese str, la base de datos tiene algunos errores 
                continue
            if dosisEspecieDict['categoria'] in especies:
                prescripciones.append(prescripcionDict)
                break
    return prescripciones

def dict_meds(prescripciones: list, especies: list, reaccionesAdversas: dict): # aqui tuve que añadir este nuevo parámetro reaccionesAdversas xq sino no funcionaba
    """
    Para obtener un diccionario de medicamentos filtrado por especies. En las cuales tendremos los siguientes keys: Medicamento, Especie de destino y Reacciones Adversas

    Args:
        prescripciones: la lista de diccionarios con toda la información
        especies: la especie que quiero analizar
        reaccionesAdversas: diccionario necesario para poder filtrar más y tener un dict nuevo específico con este parámetro adjunto

    Returns:
        Un diccionario filtrado por especie con estas keys: Medicamento, Especie de destino y Reacciones Adversas. Además de los medicamentos que solo sí esten comercializados
    """
    Dict_meds_esp = {
        "Medicamento":[],
        "Especie de destino":[],
        "Reacciones Adversas":[]
        }
    for prescripcionDict in prescripciones:
        if prescripcionDict['comercializado']=='NO': # especifíco que solo los quedamos con los que sí se comercializan
            continue
        if not 'dosisrecomendadaespecie' in prescripcionDict:
            continue
        for dosisEspecieDict in prescripcionDict['dosisrecomendadaespecie']:
            if type(dosisEspecieDict) == str: # esto daba un error si no se especificaba que fuese str, la base de datos tiene algunos errores 
                continue
            if dosisEspecieDict['categoria'] in especies: #observamos según las especies de nuestra lista  si nos quedamos con los medicamentos o no

                Dict_meds_esp['Medicamento'].append(prescripcionDict['nombre_med'])
                Dict_meds_esp['Especie de destino'].append(dosisEspecieDict['categoria'])
                
                # REACCIONES
                reaccion = '' # necesito darle un valor inicial para que pueda funcionar, porque puede estar vacía
                if 'reaccionesadversasespecie' in prescripcionDict:
                    for reaccionesDict in prescripcionDict['reaccionesadversasespecie']:
                        if type(reaccionesDict) == list or type(reaccionesDict) == str: #problema similar al anterior, en el que solo quiero quedarme con los dict 
                            continue
                        reaccion = obtener_reaccion(reaccionesDict['id_signo'], reaccionesAdversas) # llamo a la función obtener_reaccion(). Aqui tambn añado el parámetro reaccionesAdversas x la función de antes q la necesita
                        Dict_meds_esp['Reacciones Adversas'].append(reaccion) # lo añado al diccionario nuevo
                        break

                if not reaccion:
                    Dict_meds_esp['Reacciones Adversas'].append('Ninguna') # como no todos los medicamentos tienen reacciones tengo que añadir un valor "nulo" para que los parámetros me queden iguales, sino me da error
                
    return Dict_meds_esp

