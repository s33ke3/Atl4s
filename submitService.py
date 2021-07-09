import os
import requests
import time
import configparser
import json
from re import split
from shutil import copyfile
from functions import getDateTimeReadable

class ResultLog:
    Date = None
    Flags = []    

#Classe che identifica il risultato dell'invio della flag
class SubmitResult: 
    flags = []
    status = False

     

#Funzione per l'invio delle flag al Game Server
#
#Parameters: 
#
#apiUrl: Indirizzo del endpoint
#teamToken : Il Team Token 
#flags: Array contenente le flag da inviare
def submitFlag(apiUrl, teamToken, flags):
    #Invio all'API del Game Server
    r = requests.put(apiUrl, 
            headers = {
                'X-Team-Token': teamToken
            }, json=flags)
    #Creazione Istanza del risultato e impostazioni parametri
    result = SubmitResult()
    result.flags = flags
    result.status = r.status_code == 200

    return result 

def SubmitService(outputPath, sleepTime):

    #Istanzia la classe per leggere il file di configurazione
    config = configparser.ConfigParser()
    #Carica il file di configurazione
    config.read('atl4s.config')
    #Directory dove esporre l'output degli script
    exploitResultDir = config['GENERAL']['ExploitResultPath']
    #Url dell'API del Game Server
    gameServerApiUrl = config['GENERAL']['GameServerApiUrl']
    #Team Token
    teamToken = config['TEAM']['Token']
    #Nome del file di log degli invii al server
    flagsSubmittedFileName = "submittedFlags.txt"
    #Nome del file di log degli errori al server
    flagsErrorFileName = "errorSubmittedFlags.txt"

    while True:

        print("SubmitService started (loop every " + str(sleepTime) + " seconds")
        print("At " + getDateTimeReadable())

        if os.path.isfile(outputPath + "flagsToSubmit.txt"): 

            copyfile(outputPath + "flagsToSubmit.txt", 
                    outputPath + "_flagsToSubmit.txt")
            
            oldF = open(outputPath + "flagsToSubmit.txt", "w")
            oldF.close()

            if os.stat(outputPath + "_flagsToSubmit.txt").st_size > 0:
                with open(outputPath + "_flagsToSubmit.txt", "r") as f:

                    flagsToSend = []
                    line = f.readline()
                    while line:
                        pars = line.split("|")
                        flags = pars[2].split(",")

                        for flag in flags:
                            flagsToSend.append(flag)

                        line = f.readline()

                resultLog = ResultLog()
                resultLog.Date = getDateTimeReadable() 
                resultLog.Flags = flagsToSend

                # Apre in append il file delle flag trovate
                with open(exploitResultDir + flagsSubmittedFileName, 'a') as fflag:
                    json.dump(resultLog.__dict__, fflag, indent=3)
                
                #Se sono state trovate flags fa il submit massivo
                result = submitFlag(gameServerApiUrl, 
                                    teamToken, 
                                    flagsToSend)                

                os.remove(outputPath + "_flagsToSubmit.txt")

        time.sleep(int(sleepTime))
        