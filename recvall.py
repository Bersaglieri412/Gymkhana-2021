def recvall(sock):
    buffer=32
    received=''
    while(1):
        try:
            data=sock.recv(buffer)
            if not data: 
                print("hola")
                break
            received=received+data.decode()
            print(data)
        except UnicodeDecodeError:
            received=received+data.decode('utf-16')
    
    return received