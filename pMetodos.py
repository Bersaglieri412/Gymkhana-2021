#!/usr/bin/python3

from operator import index
import socket
import sys

received=b"identifier:hola\nsf"
posicionf=received.index(b'identifier:')
c=received[posicionf]
posicionf=posicionf+len(b'identifier:')
posicioni=posicionf
while posicionf<len(received) and c !=32 and c != 10 and c != 9:
    c=received[posicionf]
    posicionf=posicionf+1
posicionf=posicionf-1
print(received[posicioni:posicionf])