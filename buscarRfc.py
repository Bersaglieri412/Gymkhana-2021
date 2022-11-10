#!/usr/bin/python3

recv=b'rfc793.txt HTTP/1.1\r\nAccept-Encoding: identity\r\nHost: 10.20.10.9:10002\r\nUser-Agent: Yinkana/2020 web client\r\nConnection: close\r\n\r\n'

print(recv[3:recv.find(b'.txt')])