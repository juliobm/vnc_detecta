# vnc_detecta
Emails de aviso si se detecta diversas conexiones al servidor

### Qué hace ###


* Script en python para servidores o equipos windows. 
* Detecta conexiones a puertos como vnc o escritorio remoto, así como procesos en ejecución por conexión como el teamviewer o el gotoassist, o eventos de windows como inicio de sesión. 
* En caso de encontrar alguna conexión, envia un email a un destinatario con el tipo de conexión, la ip que lo realiza y los procesos en ejecución en ese momento.
* Se guarda un log de las conexiones.
* Se debe poner en tareas programadas para que se ejecute cada minutos que se desee pero solo mandará un email con el mismo contenido cada hora para evitar repeticiones.
* Se pueden especificar excepciones por ip.
* Se puede evitar el envio de email a puertos, procesos o eventos pero que si guarde log.

### Instalación ###

* Bajar los dos scripts en python
* Configurar el fichero .conf con nuestros datos de email, así como los puertos, procesos y eventos a vigilar.
* Poner en tareas programadas vnc_detecta.pyw.

### Dependencias ###

* Se requiere python 2.x descargable en https://www.python.org/download/
* Se requiere además para la lectura de los eventos windows pywin32 descargable en http://sourceforge.net/projects/pywin32/files/pywin32/
