#!/usr/bin/python3

frase="the cake 22 is a 305 lie 5 anna tiger 50 ..."
sep=frase.split()

for i in sep:
    if(not i.isdigit()):
        if(len(i)>1):
            if(str(i) == str(i)[::-1]):
                frase=frase[:frase.index(i)]
                break
print(frase)
