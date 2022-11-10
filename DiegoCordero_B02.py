#!/usr/bin/python3
"Internet checksum algorithm RFC-1071"
# from scapy:
# https://github.com/secdev/scapy/blob/master/scapy/utils.py

import base64
import hashlib
import socket
import struct
import sys
import array
import threading
import time
import requests

enc="-1"
#Funciones principales de cada reto
#Para la función del reto 1, simplmente creamos los sockets precedentes y hacemos lo que se nos pide en el enunciado
def reto1():
    #Reto 1
    sock = socket.socket()
    sock.connect(("rick",2000))

    received=sock.recv(1024)
    sock.send(b"hardcore_perlman")
    received=sock.recv(1024)
    print(received.decode())


    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockUDP.bind(('',11111))
    identificador= encontrar_Identificador(received)
    enviar= b'11111 '+identificador

    sockUDP.sendto(enviar,("rick",4000))
    received,server=sockUDP.recvfrom(1024)
    print(received.decode())

    identificador=identificador.upper()
    sockUDP.sendto(identificador,server)


    received,server=sockUDP.recvfrom(1024)
    print(received.decode())
    sockUDP.close()
    return received
    #Fin reto 1

#Para el reto 2 tenemos las funciones auxiliares encontrarCompanion y por primera vez el recvAll, que nos permitirán saber cuantas cajas hay
#antes de cada torreta, o, en el caso de la segunda, saber cuando dejar de recibir un mensaje porque ya tenemos un mensaje completo 
def reto2(id):
    sock = socket.socket()
    sock.connect(("rick",3006))
    identificador=encontrar_Identificador(id)+b' '
    cajas=encontrarCompanion(recvall(sock))
    print(cajas)
    identificador=identificador+cajas.encode()+b' --'
    sock.sendall(identificador)
    return sock
    #Fin reto 2

#Para el reto tres tenemos las funciones complementarias de encontrarPalindromo y reverseNumbers, que nos permitirán cumplir con lo establecido en el enunciado
#una vez hemos recibido todo el mensaje a procesar
def reto3(sock):
    data=sock.recv(1024)
    print(data.decode())
    sock1 = socket.socket()
    sock1.connect(("rick",6520))
    received=recvall(sock1)
    enviar=encontrar_Identificador(data)+b' '
    frase=encontrarPalindromo(received.decode())
    frase=reverseNumbers(frase)
    enviar=enviar+frase.encode()+b' --'
    sock1.sendall(enviar)
    return sock1
    #Fin reto 3

#Para este reto no tenemos función auxiliar, ya que nos mandan un mensaje, nosotros averiguamos su longitud y procedemos a codificarlo como procede en el 
#mismo cuerpo de la función
def reto4(sock1):
    data=sock1.recv(1024)
    print(data.decode())
    enviar = encontrar_Identificador(data)
    sock1.close()
    sock = socket.socket()
    sock.connect(("rick",9003))
    sock.send(enviar)
    received = sock.recv(1024)
    separado=received.decode('ascii', 'ignore').split(':')
    print("Tamaño: ",separado[0])
    s=int(separado[0])
    rec=b''
    while len(rec)<(s-len(received)-(len(separado[0])+1)):#Para recibir el resto del mensaje se le restará al tamaño proporcionado lo que ya hemos conseguido menos los bytes que nos proporcionan el tamaño y los ':'
        rec=rec+sock.recv(1024)
    received =received+rec
    print(len(separado[0]))
    sha1 = hashlib.sha1()
    sha1.update(received[(len(separado[0])+1):])
    sock.sendall(sha1.digest())
    return sock, received[(len(separado[0])+1):]
    #Fin reto 4

#En este reto 5 pasa algo parecido a lo anterior, ya que úniicamente tendremos que empaqeutar todo en un struct y está todo en el cuerpo de la función principal.
#Cabe resaltar que cuadno decimos que no tiene uso de ninguna función complmentaria, nos refermimos a una función específica del reto, ya que esta hace uso por ejemplo
# de la función encontrar_identificador
def reto5(sock,decoded):
    received=recvall(sock)
    sock.close()
    print(received.decode('ascii', 'ignore'))
    print(decoded[:10])
    payload=encontrar_Identificador(received[:50])
    paquete=struct.pack('!3sBHHH',b'WYP',0,0,0,1)
    payload=base64.b64encode(payload)
    enviar=paquete+payload
    checksum=cksum(enviar) #Primero haremos el cheksum de el struct con su campo a 0
    paquete=struct.pack('!3sBHHH',b'WYP',0,0,checksum,1)
    enviar=paquete+payload

    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockUDP.sendto(enviar,("rick",6000))
    received=sockUDP.recv(2048)
    payload = base64.b64decode(received[10:len(received)]).decode("UTF-8")
    return payload
    #Fin reto 5
#Para este reto haremos sobretodo uso de dos funciones, la de iniciarServer, y éste a su vez hará uso de la función peticiones, explicadas más a fondo en su lugar,
# cada una se encarga respectivamente de crear un servidor y hacer que se atiendan concurrentemente sus peticiones.
def reto6(payload):
    print(payload)
    id = encontrar_Identificador(payload.encode())
    serv_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,proto=0)
    id=iniciarServer(serv_sock,id,10000)
    return id
    #fin reto 6

#Para este reto únicamente tendremos que crear un socket, enciar por el el identificador recibido en el anterior y recibir de vuelta el final de la yimkana
def reto7(id):
    sock1 = socket.socket()
    sock1.connect(("rick",33333))
    sock1.sendall(id.encode())
    print(sock1.recv(1024).decode())
    #Fin reto 7

#Funciones en general de los retos y complementarias a todos:
#Funciones auxiliares generales
#Esta función en concreto busca al prinicpio de cada linea de un menasaje el identificador.
def encontrar_Identificador(received):
    received=received.decode('ascii', 'ignore')
    l=received.splitlines()
    i=len(l)-1
    devolver=''
    while(i>=0):
        if(l[i].startswith('identifier:')):
            devolver=l[i][len(b'identifier:'):]
        i-=1

    return devolver.encode()

#Método creado para recibir todo un mensaje cuando no se tiene un final de éste claro. En este caso lo que hará será estar escuchando constantemente
#hasta que pase un segundo sin recibir nada, en ese momento se sabrá que ya no se va a recibir ningún bloque más y se enviará todo lo recopilado
#hasta ese entonces. Está hecho a raiz del reto 2, podría habere estado escuchando ahsta que en un bloque se encontrase la "torreta", pero he pensado
#que sería más general si en vez de aplicarlo para el reto 2 sirviera a priori para más retos
def recvall(sock):
    buffer=512
    received=''
    bloques=[]
    try:
        sock.settimeout(1)
        while(1):
            data = sock.recv(buffer)
            if not data: 
                break
            bloques.append(data)
            #print(data)
            
    except socket.timeout: #Cuando salte el timeOut del socket, este lanzará una excepción.Excepción que nosotros capturamos y usamos para resetear el timeOut a 5 segundos y terminar el bucle
        sock.settimeout(5)
        pass        
    
    return b"".join(bloques)

#Función para el reto 1, simplmente busca de entre todo el mensaje la palabra palíndroma primera y nos devuelve hasta ese punto
def encontrarPalindromo(frase):
    sep=frase.split()

    for i in sep:
        if(not i.isdigit()):
            if(len(i)>1):
                if(str(i) == str(i)[::-1]):
                    frase=frase[:frase.index(i)]
                    break
    return frase

#Función para el reto 2, como no podemos decodificar el código debido a errores con el formato de mensaje, codificaremos lo que tenemos que buscar
#y lo buscaremos en el propio código codificado
def encontrarCompanion(receive):
    caja="[❤]"
    torreta="╭(◉)╮"
    caja=caja.encode()
    torreta=torreta.encode()
    try: 
        buscar=receive[0:receive.index(torreta)]
    except ValueError:
        buscar=receive
        pass

    contador=0

    while(True):
        try: 
            buscar=buscar[(buscar.index(caja)+len(caja)):]
            contador=contador+1                  
        except ValueError:
            break

    devolver=''
    while(contador!=0):
        devolver=devolver+'[❤]'
        contador=contador-1
    return devolver
#Función para el reto 3, únicamente se separará lo que se mande dependiendo de las palabras y se aplicará
#La lógica necesaria para superar el enunciado
def reverseNumbers(frase):
    separado=frase.split()
    bloque=[]
    for i in separado:
        if(i.isalpha()): 
            bloque.append(i)

    bloque=bloque[::-1]
    contador=0
    for i in range(0,len(separado)):
        if(separado[i].isalpha()):
            separado[i]=bloque[contador]
            contador=contador+1
        else:
            separado[i]=separado[i][::-1]

    frase = ' '.join(separado)
    return frase

#Función complmentaria reto 5
def cksum(pkt):
    # type: (bytes) -> int
    if len(pkt) % 2 == 1:
        pkt += b'\0'
    s = sum(array.array('H', pkt))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    s = ~s

    if sys.byteorder == 'little':
        s = ((s >> 8) & 0xff) | s << 8

    return s & 0xffff

#Funciones necesarias para el reto 6
#la función iniciarServer, crea a raíz de un puerto y un socket un server que estará siempre a la escucha. Podríamos haber creado el socket directamente desde
# el propio método, pero esto nos habría impedido poder llamarla recursivamente y cambiar el puerto ene stas llamadas si hiciere falta, como explicamos al final
#de esta función
def iniciarServer(serv_sock,id,puerto):
    try:
        serv_sock.bind(('10.20.10.9', puerto))
        sock= socket.socket()
        sock.connect(("rick",8002))
        sock.sendall(id+b' '+str(puerto).encode())
        serv_sock.settimeout(1)
        serv_sock.listen(10)
        i=0
        hilo = []
        
        while enc=="-1":  
            try:  
                client_sock, client_addr = serv_sock.accept()
                hilo.append(threading.Thread(target =peticiones,args=(client_sock,)))
                hilo[i].start()
                i+=1
                time.sleep(0.2)
            except socket.timeout:  #Mismo uso que en la función recvall
                pass
            except KeyboardInterrupt:
                pass

        serv_sock.settimeout(5) 
        serv_sock.close()   
        for i in hilo: #Este bucle nos ayudará a unir los hilos que hemos creado al hilo prinipal, eliminando aquellos que por algún motivo no se hayan cerrados solos
            i.join()
            
        return enc
        
    except OSError: #Si acaso se ejecutase el programa muy de sguido es bastante probable que el socket del seridor no le haya dado tiempo a cerrarse, por lo que se asigna un nuevo puerto para que funicone
        print("La dirección propuesta ya estaba en uso, se intentará con otra")
        return iniciarServer(serv_sock,id,puerto+1)
    except KeyboardInterrupt:
        print("Se ha cerrado el programa")

#Esta función se encarga de atender todas las peticiones que se le van haciendo concurrentemente, dsitinguiendo primero el tipo de ejcución (una normal get o una final)
# y después atendiéndola y proporcionándole el ok correspondiente.
def peticiones(client_sock):
    global enc
    global iden
    recv=(recvall(client_sock))
    if "identifier:" in recv.decode(): #Si en el mensaje de petición se encuentra el enunciado del reto 7, entonces la petición será post, por lo que se realizará de diferente manera
            print("Mensaje encontrado en el hilo ",threading.current_thread().getName())
            print(recv.decode())
            rfc=(recv[(recv.find(b'rfc')+3):recv.find(b'.txt')])
            rfc=rfc+b'.txt'
            post=requests.post(b"http://rick:81/rfc/rfc"+rfc)  
            request = ("HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\nContent-Length: "+str(len(post.text.encode("utf-8")))+"\n\n").encode("utf-8") 
            client_sock.sendall(post.text.encode("utf-8"))
            client_sock.sendall(request)
            enc=encontrar_Identificador(recv).decode()
              
  
    else:
            print("Hilo: ",threading.current_thread().getName()) 
            rfc=(recv[(recv.find(b'rfc')+3):recv.find(b'.txt')])
            rfc=rfc+b'.txt'
            print(recv.decode())
            get=requests.get(b"http://rick:81/rfc/rfc"+rfc)  
            request = ("HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\nContent-Length: "+str(len(get.text.encode("utf-8")))+"\n\n").encode("utf-8") 
            client_sock.sendall(request)
            try:
                client_sock.sendall(get.text.encode("utf-8"))
            except BrokenPipeError: #Este except es debido a que el socket del cliente, tras muchas peticiones se cerraba esporádcicamente, he asumido que se trataba
                                    #de un caso en el qeu ya no quería la petición o de pura saturación, por lo que ignorando el error se solucionó
                pass

#Función "main", cada función de reto, genera un identificador o un socket que utilizará una reto superior, por lo que todas salvo la primera y la última,
#devuelven o reciben un identificador/socket, de manera que  todos los retos queden comunicados
try:
    id1=reto1()
    sock=reto2(id1)
    sock3=reto3(sock)
    sock4,r=reto4(sock3)
    id5=reto5(sock4,r)
    id6=reto6(id5)
    reto7(id6)
except KeyboardInterrupt: #Por si se pulsara ctr+c en algún momento del programa
    print("Se saldrá del programa")

sys.exit(0)




