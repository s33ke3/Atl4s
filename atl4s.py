from datetime import datetime
from submitService import SubmitService
from subprocess import STDOUT
from functions import getDateTimeString
from functions import executeScript
from threading import Thread
import os
import sys
import time
import configparser

#Istanzia la classe per leggere il file di configurazione
config = configparser.ConfigParser() 
#Carica il file di configurazione
config.read('atl4s.config') 
# Recupera il path del logfile (se presente)
logFilePath = config['GENERAL']['LogFile'] 

#Se non presente lo ridirige sullo standard output
logFileStream = sys.stdout 
if logFilePath != "":
    logFileStream = open(logFilePath, "w") 

print("""
*******************************************************************************************
&			    ___  __  ______   	  					  &
&			   / _ |/ /_/ / / /___		  				  &
&			  / __ / __/ /_  _(_-<		  				  &
&			 /_/ |_\__/_/ /_//___/	Ver 1.7	   				  &
&			  @@@@@Created by@@@@@@		   			          &
&			   -->Davide Bovio<--              				  &
&			 -->Vincenzo Digilio<--  	  				  &
&	 							 			  &
&              **with Hacking Team @PGiatasti - Università di Perugia**			  &
&		         								  &
*******************************************************************************************
""", file=logFileStream)
							 
#Path dell'eseguibile di python
pythonPath = config['GENERAL']['PythonExec']
# Directory che contiene Exploit e lista degli Exploit da eseguire 
exploitDir = config['GENERAL']['ExploitPath']
#Directory dove esporre l'output degli script
exploitResultDir = config['GENERAL']['ExploitResultPath'] 
# Numero di secondi tra un ciclo e l'altro
sleepTime = config['GENERAL']['SleepSeconds']
# Numero di secondi tra un ciclo e l'altro del servizion di invio flags
sleepServiceTime = config['GENERAL']['SleepServiceSeconds']
# Variabile che contiene il nome "costruito" per l'output dello script
outputFileName = "" 

global lastSendFlag

#Cicla indefinitamente
while True:

    #Lancia il servizio di polling per l'invio delle flag
    tss = Thread(target=SubmitService, args=[exploitResultDir, sleepServiceTime])
    tss.start()

    # Recupera l'elenco degli IP da attaccare in una lista
    ipList = []
    with open('ipList.txt') as f:
        for line in f:
            ipList.append(line.strip())

    # Recupera l'elenco degli exploit selezionati da utilizzare
    # Gli exploits devono essere script python
    exploitList = []
    with open(exploitDir + 'exploitList.txt') as f:
        for line in f:
            exploitList.append(line.strip())
    
    # Per ogni Exploit da eseguire
    for exploit in exploitList:    

        #Splitta gli elementi della linea che ha trovato nel file di testo degli Exploit da eseguire   
        exploitPars = str(exploit).split(' ')
        #Il primo elemento è sempre il nome dell'Exploit da eseguire
        exe = exploitPars[0]
        #Prende i restanti parametri da passare
        defaultPars = ' '.join(exploitPars[1:])

        #Per ogni ip presente nel file iplist.txt    
        for ip in ipList:
            #Sostituisce la costante [ip] con l'ip bersaglio 
            pars = defaultPars.replace('[ip]', ip)
            #Costruzione del file di Output
            outputFileName = exe + '_' + str(ip) + '_' + getDateTimeString() + ".txt"
            #Esegue la funzione executeScript in un Thread separato, passando il nome funzione in target e la lista degli
            #argomenti della funzione in args.
            process = Thread(target=executeScript, 
                             args=[pythonPath + ' ' + exploitDir + exe + ' ' + pars, 
                                  exploitResultDir, 
                                  outputFileName, 
                                  logFileStream])                               
            
            #Fa partire il Thread
            process.start()
    
    #Attendi 'sleepTime' prima del ciclo successivo
    time.sleep(int(sleepTime))
