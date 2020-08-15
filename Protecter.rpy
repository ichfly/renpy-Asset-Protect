init python:
    #Start DRM
    import subprocess
    import hashlib
    import random
    import struct
    import threading
    import base64
    
    proc = subprocess.Popen('test.exe', 
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        )
                        
    #just obfuscation for cmd sniffer/replayer replace with your own key handshake start DRMREPLACME <at least replace the constants 13/7/SECKEY/0x16/0x24/0x53/2 in keyupdate also in PC>
    #dose not need to be save just obfuscated
    #DRM use config.file_open_callback if you dont want to allow people to change files or also protect other files
    #config.periodic_callback is also a good idea for checking for changes

    SECKEY1 = [123, 175, 106, 144, 225, 102, 194, 195, 229, 105, 213, 122, 32, 146, 15, 9, 161, 104, 151, 63, 167, 54, 152, 140, 200, 59, 100, 57, 111, 223, 215, 70, 6, 247, 190, 71, 186, 127, 134, 10, 34, 207, 67, 3, 164, 147, 4, 126, 138, 109, 124, 74, 101, 174, 240, 114, 49, 220, 41, 135, 137, 153, 35, 80, 13, 42, 162, 93, 141, 92, 172, 23, 116, 158, 136, 98, 43, 199, 212, 182, 132, 192, 18, 185, 24, 14, 91, 39, 77, 7, 89, 202, 69, 95, 218, 28, 155, 252, 21, 97]
    SECKEY2 = [196, 208, 139, 228, 134, 191, 6, 144, 193, 2, 65, 241, 125, 106, 189, 145, 24, 104, 73, 98, 171, 225, 109, 214, 101, 175, 229, 143, 141, 33, 107, 182, 105, 152, 131, 41, 22, 162, 70, 77, 129, 30, 165, 126, 207, 151, 50, 136, 21, 49, 137, 237, 75, 133, 56, 68, 220, 44, 185, 91, 172, 180, 192, 179, 83, 118, 132, 92, 29, 17, 215, 155, 209, 99, 60, 149, 5, 45, 43, 79, 115, 1, 255, 238, 87, 20, 217, 248, 232, 168, 121, 199, 111, 161, 123, 253, 78, 67, 72, 117]
    DRMkey = proc.stdout.readline()
    DRMkey = base64.b64decode(DRMkey)
    DRMkey = [ord(x) for x in DRMkey]

    for i in range(100):
        keyPart = random.randrange(0,255)
        if i % 13 == 0:
           DRMkey[i] = DRMkey[i] ^ SECKEY1[i]
        elif i % 7 == 0:
            DRMkey[i] = keyPart
        else:
            DRMkey[i] = DRMkey[i] ^ SECKEY1[i] ^ keyPart
        tosend = base64.b64encode(struct.pack("B", (keyPart ^ SECKEY2[i])))
        proc.stdin.write(tosend + "\n")
    

    def crypt(data):
        tKey = DRMkey
        for i in range(len(data)):
            tk = ((tKey[0] ^ tKey[0x16] ^ tKey[0x24] ^ tKey[99]) + 0x53) % 255
            for j in range(99):
                tKey[j] = tKey[j + 1]
            tKey[99] = tk
            
            data[i] = data[i] ^ DRMkey[2]
        DRMkey = tKey
        return(data)
    #just obfuscation for cmd sniffer/replayer replace with your key handshake own end
    lockDRM = threading.Lock()
    def toByte2(data):
        return struct.pack('B' * len(data), *data)
       
    
    def LoadOBFUS(path):        
        pathorig = path
        path = path.replace("/", "\\")
        #? is already a hash ? is not allowed in File names
        tosend = None
        if path.startswith("?"):
            tosend = bytearray.fromhex(path[-1:])
        else: #hash
            m = hashlib.sha256()
            m.update(path)
            tosend = m.digest()
        tosend = [ord(x) for x in tosend]

        lockDRM.acquire()
        f=open("guru99.txt", "a+")
        f.write("open: " + (str)(path) + "\n")
        f.close()
        
        proc.stdin.write(base64.b64encode(toByte2(crypt([0x42]))) + "\n") #read file request
        proc.stdin.write(base64.b64encode(toByte2(crypt(tosend))) + "\n")
        proc.stdin.flush()
        while True:
            test = base64.b64decode(proc.stdout.readline())
            test = [ord(x) for x in test]
            Cmd = (crypt(test))[0]
            
            temp = base64.b64decode(proc.stdout.readline())   
            if (Cmd & 0x80) == 0:           
                temp = [ord(x) for x in temp]
                temp = crypt(temp)
                temp = toByte2(temp)
            Cmd = Cmd & 0x7F
            try:
                if Cmd == 0x42: #request response
                    data = temp
                    break
                elif Cmd == 0x3: #read
                    temp = (str)(temp.decode("ASCII"))
                    tosend = (str)(globals()[temp])
                    tosend = [ord(x) for x in tosend]
                    proc.stdin.write(base64.b64encode(toByte2(crypt(tosend))) + "\n")
                elif Cmd == 0x48: #exec
                    temp = (str)(temp.decode("ASCII"))
                    exec(temp)
                elif Cmd == 0x9: #eval
                    temp = (str)(temp.decode("ASCII"))
                    tosend = eval(temp)
                    tosend = [ord(x) for x in tosend]
                    proc.stdin.write(base64.b64encode(toByte2(crypt(tosend))) + "\n")
            except:
                if (Cmd & 0x40) == 0:
                    tosend = "error except"
                    tosend = [ord(x) for x in tosend]
                    proc.stdin.write(base64.b64encode(toByte2(crypt(tosend))) + "\n")

        lockDRM.release()
        if len(data) == 0:
            return None
        else:
            res = im.Data(data,pathorig)
            return res

    def LoadMissingShow(name, what, layer):
        temp = ""
        for i in name:
            temp += " " + i.encode("ASCII")
        
        return LoadOBFUS(temp[1:])
    
    def LoadMissingImage(path):
        return LoadOBFUS(path)
    #config.debug = True
    config.missing_show = LoadMissingShow
    config.missing_image_callback = LoadMissingImage
    #End DRM
