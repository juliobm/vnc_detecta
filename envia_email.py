#-------------------------------------------------------------------------------
# Name:        envia_email
# Purpose:     atencion: cuidado con la copia oculta bcc
#              solo se oculta en las cabeceras pero puede verse en
#              opciones del documento. NO UTILIZAR
#
# Author:      JULIO
#
# Created:     20/06/2011
# Copyright:   (c) JULIO 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import smtplib, sys, subprocess, os

from email.Parser import Parser
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
from email.Utils import COMMASPACE


def mandaemail(user, passw, mismtp, to, subject, text, adjunto= '', cc = [], bcc = []):
    """ manda emails con datos recogidos por parametros
    o funcion importada
    diferenciacion gmail
    """

    msg = MIMEMultipart()
    textomsg=MIMEText(text)
    msg['Subject']=subject
    msg['From']=user

	if (type(to) is str):
		to = [to]
    msg['To']= COMMASPACE.join(to)
    msg['cc'] =  COMMASPACE.join(cc)
    msg['Bcc'] =  COMMASPACE.join(bcc)
    '''
    msg['To']= to
    msg['cc'] =  cc
    msg['Bcc'] =  bcc
    '''

    todos = to
    if cc <> []: todos = todos + cc
    if bcc<> []: todos = todos + bcc

    msg.attach(textomsg)

    if adjunto<>"":
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(adjunto,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                            % os.path.basename(adjunto))
        msg.attach(part)

    if user.find('gmail.com')<> -1 :
        smtp=smtplib.SMTP('smtp.gmail.com',587)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
    else:
        smtp=smtplib.SMTP(mismtp)

    smtp.login(user,passw)
    try:
        smtperror = smtp.sendmail(msg['From'], todos, msg.as_string())
    except:  # SMTPDataError:
        #print errstr
        pid2=subprocess.call('echo ERROR ' + str(subject)+ ' '+ str(todos) +' >>envia_email_error.txt',shell=True)
        pass

    smtp.close()


if __name__ == '__main__':
    print len(sys.argv)
    if len(sys.argv)<7:
        print 'Argumentos requeridos: usuario contra smtp destino asunto texto [adjunto=] [bcc=]'
        exit()
    mandaemail(*sys.argv[1:])


