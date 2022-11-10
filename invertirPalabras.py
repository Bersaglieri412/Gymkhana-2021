#!/usr/bin/python3

from os import sep


def palindromo(frase):
    sep=frase.split()

    for i in sep:
        if(not i.isdigit()):
            if(len(i)>1):
                if(str(i) == str(i)[::-1]):
                    frase=frase[:frase.index(i)]
                    break
    return (frase)


frase="the cake 22 is a 305 lie 5 anna tiger 50 ..."
frase=palindromo(frase)
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
print(frase)
