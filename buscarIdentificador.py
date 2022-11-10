#!/usr/bin/python3

received="upper-code?\nidentifier:63a11f7a-2\n\n\nWelcome to the test chamber number 2. You're doing quite well.\nExcellent work. As part of a"

l=received.splitlines()
i=len(l)-1
while(i>=0):
    if(l[i].startswith('identifier:')):
        devolver=l[i][len(b'identifier:'):]
    i=i-1

print(devolver)
