#-------------------------------------------------------------------------------
# Name:        vnc_detecta
# Purpose:     email aviso conexiones al puerto 3389, 47195, 5900
#               propios de escritorio remoto o vnc
#               solo manda un email de aviso cada hora
#               con los procesos del sistema ejecutÃ¡ndose en ese momento
#               pero se guarda log cada vez que se detecta
# Author:      JULIO
#
# Created:     17/06/2011
# Copyright:   (c) JULIO 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import time,datetime,os,sys,subprocess
import win32evtlog # requires pywin32 pre-installed
import smtplib, ConfigParser
import random, socket

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from envia_email import mandaemail

def main():
    pass

if __name__ == '__main__':
    main()

nombre = socket.gethostname()
ip_local = socket.gethostbyname_ex(socket.gethostname())[2][0]

fic_error = open('vnc_detecta_'+ nombre + '_error.txt','a')
fic_log = 'vnc_detecta_' + nombre + '_log.txt'
fic_log_proceso = 'vnc_detecta_pro_' + nombre + '_log.txt'
fic_temp = 'vnc_detectado_' + nombre + '_temp.txt'
fic_temp_proceso = 'vnc_detectado_pro_' + nombre + '_temp.txt'
dt = datetime.datetime.now()

conf = 'vnc_detecta_conf.txt'
if not os.path.exists(conf):
    print 'Falta fichero configuraciÃ³n'
    exit()

ficini = ConfigParser.ConfigParser()
ficini.read(conf)
if not ficini.has_section('principal'):
    print 'Faltan datos principales'
    exit()
emailuser = ficini.get('principal', 'u')
emailpassw = ficini.get('principal', 'p')
emailpop3 = ficini.get('principal', 'pop3')
emailssl = ficini.get('principal', 'ssl')
emailsmtp = ficini.get('principal', 'smtp')
emailaquien = ficini.get('principal', 'aquien').split(',')
emailsi = ficini.get('principal', 'emailsi')

puertos = ficini.items('puertos')
procesos = ficini.items('procesos')
formato_es = '%d/%m/%y %H:%M:%S'
formato_en = '%m/%d/%y %H:%M:%S'
formato =formato_en
try:
    eventos = ficini.items('eventos')
    formato = ficini.get('principal','formatofecha')
except:
    pass

excepciones=[]
try:
    excepciones = ficini.items('excepciones')
except:
    pass

for puerto in puertos:
    sentencia='netstat -no|find "'+ ip_local + ':' + puerto[0] + '"'
    pidc = subprocess.Popen(sentencia,shell=True,stdout=subprocess.PIPE,stderr=fic_error) # con esto esperamos a que termine antes de seguir con el siguiente
    hay=pidc.stdout.readlines()
    if len(hay)>0:
    	fich_log = open(fic_log,"a+")
    	for row in hay:
            ip = row.split()[2]
            ip = ip.split(":")[0]
            salimos = False
            for exc in excepciones:
                if exc[0] == ip:
                    salimos = True
            if salimos:
                break
            ip = ip.replace(".","_")
            #ip = ip + '_en_' + puerto
    	    fich_log.write(nombre + '_acceso_'+ str(dt) + '_' + row[:-2]+' '+'\n')
            fich_temp = open(fic_temp,"w+")
            fich_temp.write(nombre + '_acceso_'+ str(dt)+'_'+row[:-2]+' '+'\n')
            fich_temp.close()
            # flag para no repetir cada hora
            fic_flag = 'vnc_detectado_'+ nombre + '_' + puerto[0] + '_' + dt.strftime("%Y%m%d_%HH")+'_ip_'+ ip + '.txt'
            if (os.path.exists(fic_flag)==False):
                fich_flag=open(fic_flag,"w+")
                fich_flag.close()
                if puerto[0] =='3389':
                    sentencia2='tasklist /v|find /i "rdp-tcp">>'+ fic_temp
                if puerto[0] =='47195' or puerto[0] =='5900' or puerto[0] =='47196':
                    sentencia2='tasklist /v>>'+ fic_temp
                pidc1 = subprocess.Popen(sentencia2,shell=True,stderr=fic_error)
                adjunto=fic_temp
                asunto = nombre + '_acceso_'+ puerto[0] + '_'+ ip + dt.strftime("_%Y%m%d_%HH")
                texto=row[:-2]
                time.sleep(1)
                if emailsi=='si':
                    '''
                    harto de emails por simple conexiÃ³n tcp al 3389
                    de los juankers
                    '''
                    if puerto[1]<>'emailno':
                        mandaemail(emailuser, emailpassw, emailsmtp,emailaquien,asunto,texto,adjunto)
    	fich_log.close()
    	# a pelo los procesos rdp-tcp
    	if puerto[0] =='3389':
    	    sentencia2='tasklist /v|find /i "rdp-tcp">>'+ fic_log
    	if puerto[0] =='47195' or puerto[0]=='5900' or puerto[0]=='47196':
    	    sentencia2='tasklist /v >>'+ fic_log
    	pidc1 = subprocess.Popen(sentencia2,shell=True,stderr=fic_error)
        #fic_h_error.write('escritorio remoto pasado '+ str(dt) + '\n')

# ahora procesos
#C:\Program Files (x86)\TeamViewer\Version7\Connections_incoming.txt
for proceso in procesos:
    sentencia2='tasklist /v|find /i "'+ proceso[0] + '"'
    #print sentencia2
    pid = subprocess.Popen(sentencia2,shell=True,stdout=subprocess.PIPE,stderr=fic_error) # con esto esperamos a que termine antes de seguir con el siguiente
    hay=pid.stdout.readlines()
    if len(hay)>0:
    	fich_log_pro = open(fic_log_proceso,"a+")
    	for row in hay:
            pro_entero = row.split()[0]
            pro_id = row.split()[1]
            fich_log_pro.write(nombre + '_acceso_proceso_'+ proceso[0]+'_'+ pro_id + '_'+str(dt) + '_' + row[:-2]+' '+'\n')
            fich_temp_pro = open(fic_temp_proceso,"w+")
            fich_temp_pro.write(nombre + '_acceso_proceso_'+ proceso[0]+'_'+ pro_id + '_'+str(dt)+'_'+row[:-2]+' '+'\n')
            fich_temp_pro.close()
            # flag para no repetir cada hora
            fic_flag = 'vnc_detectado_pro_'+ nombre + '_' + proceso[0] + '_' + pro_id + '_'+ dt.strftime("%Y%m%d_%HH")+ '.txt'
            if (os.path.exists(fic_flag)==False):
                fich_flag=open(fic_flag,"w+")
                fich_flag.close()
                sentencia2='tasklist /v>>'+ fic_temp_proceso
                pidc1 = subprocess.Popen(sentencia2,shell=True,stderr=fic_error)
                adjunto=fic_temp_proceso
                if proceso[1]<>'': adjunto=proceso[1]
                asunto = nombre + '_acceso_proceso_'+ proceso[0] + '_'+ pro_id +'_'+ dt.strftime("_%Y%m%d_%HH")
                texto=row[:-2]
                time.sleep(1)
                if emailsi=='si':
                    mandaemail(emailuser, emailpassw, emailsmtp,emailaquien,asunto,texto,adjunto)
    	fich_log_pro.close()

#exit()
fic_error.close()

ult_evento = ['12/01/14 0:0:0']
if (os.path.exists('vnc_detecta_evento.txt')):
    fich_evento = open('vnc_detecta_evento.txt',"r")
    ult_evento = fich_evento.readlines()
    ult_evento = ult_evento[0].split(chr(9))
    fich_evento.close()
else:
    fich_evento = open('vnc_detecta_evento.txt',"w")
    fich_evento.write(dt.strftime(formato) )
    fich_evento.close()
fechaantes = datetime.datetime.strptime(str(ult_evento[0]),formato)

server = 'localhost' # name of the target computer to get event logs
logtype = 'Security' #'System' # 'Application' # 'Security'
hand = win32evtlog.OpenEventLog(server,logtype)
flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
#total = win32evtlog.GetNumberOfEventLogRecords(hand)
texto = ''
if len(eventos)>0:
    events=1
    while events:
        events = win32evtlog.ReadEventLog(hand, flags,0)
        if events:
            for event in events:
                #print events
                fecha = datetime.datetime.strptime(str(event.TimeGenerated), formato)
                if fecha <= fechaantes:
                    break
                #print event.EventID
                for miraevento in eventos:
                    if str(event.EventID) in miraevento[0]:
                        fich_evento = open('vnc_detecta_evento_temporal.txt',"a")
                        new_evento = str(event.TimeGenerated) + chr(9) + str(event.EventID)+ chr(9) + str(event.EventCategory) + chr(9) + str(event.SourceName)
                        fich_evento.write(new_evento+'\n\r')
                        data = event.StringInserts
                        if data:
                            for msg in data:
                                fich_evento.write(msg + '\n\r')
                        fich_evento.write('\n\r')
                        fich_evento.close()
                        texto = texto + '_' +str(event.EventID)

if (os.path.exists('vnc_detecta_evento_temporal.txt')):
    try:
        os.remove('vnc_detecta_evento.txt')
    except:
        pass
    finally:
        os.rename('vnc_detecta_evento_temporal.txt', 'vnc_detecta_evento.txt')
        if emailsi=='si':
            asunto = nombre + '_eventos_'+ dt.strftime("%Y%m%d_%HH")
            adjunto = 'vnc_detecta_evento.txt'
            time.sleep(1)
            mandaemail(emailuser, emailpassw, emailsmtp,emailaquien,asunto,texto,adjunto)

fich_log =open("ftp_cada_5m_do_log.txt","a+")
fich_log.write('fin vnc_detecta '+ str(datetime.datetime.now()) + '\n')
fich_log.close()
exit()
'''
                print 'Event Category:', event.EventCategory
                print 'Time Generated:', event.TimeGenerated
                print 'Source Name:', event.SourceName
                print 'Event ID:', event.EventID
                print 'Event Type:', event.EventType
                data = event.StringInserts
                if data:
                    print 'Event Data:'
                    for msg in data:
                        print msg
                print
'''
