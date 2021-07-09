import os
import re
import subprocess
import time
import configparser
from datetime import datetime

#Controlla all'interno del testo passato se presente la stringa corrispondente alla regex passata  
def findFlagsInText(text, regexpr):
    r = re.findall(regexpr, text, re.MULTILINE)
    if r == None:
        #
        return []
    else:
        return r

#Controlla se la flag è valida in base ai criteri della regular expression, indicata nel file di configurazione
def checkValidity(flag, regexpr):
    r = re.match(regexpr, flag)
    if r:
        return True
    else:
        return False   



#Funzione che ritorna la striga per data e ora, per il nome file
def getDateTimeString():
    now = datetime.now() # current date and time
    return now.strftime("%Y%m%d_%H%M%S") 
 
#Funzione che ritorna la striga per data e ora, per log file
def getDateTimeReadable():
    now = datetime.now() # current date and time
    return now.strftime("%d/%m/%Y %H:%M:%S") 

#Funzione che esegue lo script sul Target e cerca la flag all'interno dell'output generato
def executeScript(scriptPath, outputPath, outputFileName, logFileStream):
    
    #Istanzia la classe per leggere il file di configurazione
    config = configparser.ConfigParser()
    #Carica il file di configurazione
    config.read('atl4s.config')
    #Regular expression per la flag
    regexpr = config['GENERAL']['FlagRegExpr']
    
    #Inzio della procedura
    starttime = time.time()
    print("start execute " + scriptPath + getDateTimeReadable(), 
          file=logFileStream)

    #Apre il file di output in scrittura 
    with open(outputPath + outputFileName, 'w') as f:
        #Esegue lo script in un processo di Shell facendo un redirect dell'output sul file 
        subprocess.run([scriptPath], shell=True, stdout=f)
    
    #Divisione del file name per recuperare l'indirizzo IP
    filenameparts = outputFileName.split('_')

    #Apre il file di Output in lettura
    with open(outputPath + outputFileName, "r") as fout:
        flags = findFlagsInText(fout.read(), regexpr)

    #Eliminazione file di output
    os.remove(outputPath + outputFileName)        
    if len(flags) > 0:
        
        with open(outputPath + "flagsToSubmit.txt", "a") as fflag:
            print(filenameparts[1] + "|" + 
                  filenameparts[0] + "|" + 
                  ",".join(flags), file=fflag)    

    #Termine della procedura
    endtime = time.time()
    print("end " + scriptPath + " - seconds: " + 
          str(endtime - starttime), file=logFileStream)
