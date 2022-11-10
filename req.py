#!/usr/bin/python3
import requests

get=requests.get(b"http://rick:81/rfc"+b'234.txt')  
print(get.text.encode()) 