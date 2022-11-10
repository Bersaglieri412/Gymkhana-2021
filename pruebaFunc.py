#!/usr/bin/python3
"Internet checksum algorithm RFC-1071"
# from scapy:
# https://github.com/secdev/scapy/blob/master/scapy/utils.py

import base64
from hashlib import sha1
import socket
import struct
import sys
import array
import threading
import time
import requests

enc="-1"

def iniciarServer(serv_sock):
    serv_sock.bind(('10.20.10.9', 10069))
    sock= socket.socket()
    sock.connect(("rick",8002))
    sock.sendall(id+b' 10069')
    serv_sock.settimeout(1)
    serv_sock.listen(3)
    i=0
    hilo = []
    
    while enc=="-1":  
        try:  
            client_sock, client_addr = serv_sock.accept()
            hilo.append(threading.Thread(target =peticiones,args=(client_sock,)))
            hilo[i].start()
            i+=1
            time.sleep(0.1)
        except socket.timeout:  
            pass

    serv_sock.settimeout(5)    
    for i in hilo:
        i.join()
        

    return enc

def peticiones(client_sock):
    global enc
    global iden
    recv=(recvall(client_sock))
    if "identifier:" in recv.decode():
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
            client_sock.sendall(get.text.encode("utf-8"))

#Funciones auxiliares
def encontrar_Identificador(received):
    received=received.decode()
    l=received.splitlines()
    i=len(l)-1
    devolver=''
    while(i>=0):
        if(l[i].startswith('identifier:')):
            devolver=l[i][len(b'identifier:'):]
        i-=1

    return devolver.encode()

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
            
    except socket.timeout:
        sock.settimeout(5)
        pass        
    
    return b"".join(bloques)

#Función para el reto 3
def encontrarPalindromo(frase):
    sep=frase.split()

    for i in sep:
        if(not i.isdigit()):
            if(len(i)>1):
                if(str(i) == str(i)[::-1]):
                    frase=frase[:frase.index(i)]
                    break
    return frase

#Función para el reto 2
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
#Función complmentaria reto 4
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

#Reto 1
sock = socket.socket() #se crea un socket tcp  si no se pone nada
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

#Fin reto 1
#Reto 2
sock = socket.socket() #se crea un socket tcp  si no se pone nada
sock.connect(("rick",3006))
identificador=encontrar_Identificador(received)+b' '
cajas=encontrarCompanion(recvall(sock))
print(cajas)
identificador=identificador+cajas.encode()+b' --'
sock.sendall(identificador)
#Fin reto 2

#Reto 3
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
#Fin reto 3

#Reto4
data=sock1.recv(1024)
print(data.decode())
enviar = encontrar_Identificador(data)
sock1.close()
sock = socket.socket()
sock.connect(("rick",9003))
sock.send(enviar)
received = recvall(sock)
print(received[0:7])
prueba=sha1(received[7:])
pbHash = prueba.digest()
sock.sendall(pbHash)
#Fin reto 4

#Reto 5
received=sock.recv(4096)
sock.close()
print(received.decode())
payload=encontrar_Identificador(received)
type=0
code=0
sequence=1


paquete=struct.pack('!3sBHHH',b'WYP',0,0,0,1)
payload=base64.b64encode(payload)
enviar=paquete+payload
checksum=cksum(enviar)
paquete=struct.pack('!3sBHHH',b'WYP',0,0,checksum,1)
enviar=paquete+payload

sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockUDP.sendto(enviar,("rick",6000))
received=sockUDP.recv(2048)
payload = base64.b64decode(received[10:len(received)]).decode("UTF-8")
#Fin reto 5

#Reto 6
print(payload)
id = encontrar_Identificador(payload.encode())
serv_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM,proto=0)
id=iniciarServer(serv_sock)
#fin reto 6

#reto 7
sock1 = socket.socket()
sock1.connect(("rick",33333))
sock1.sendall(id.encode())
print(sock1.recv(1024).decode())

sys.exit(0)




