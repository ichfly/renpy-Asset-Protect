# -*- coding: utf-8 -*-
import glob2
import sys
import hashlib
import random
import os
import array
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
all_files = []
for i in sys.argv[3:]:
    all_files = all_files + glob2.glob(i)
all_files = list(set(all_files))
random.shuffle(all_files)

fdata = open('000.dat', 'w+b')
fhead = open("genData.hpp","w+")
currentPos = 0
entries = 0
#print(len(all_files))
iv  = bytearray([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f ])

def getProtectFile(name,key):
    res = None
    for i in range(len(name.split("\\"))):
        res = loadProtect(name + ".prot",key)
        if res != None:
            return res
        if len(name.split("\\")) != 1:
            name = name[:name.rindex('\\')]
    name = "default.prot"
    if res == None:
        return loadProtect(name,key)

def loadProtect(name,key):
    try:
        if os.path.isfile(sys.argv[2] + name) == False:
            return None
    except:
        return None
    m = hashlib.sha256()
    m.update(key)
    file=open(sys.argv[2] + name, "r")
    content = file.read()
    flagsRaw = content.splitlines()[0]
    #todo make this code better with xtend etc.
    content = content[len(flagsRaw)+1:]
    data = bytearray()
    while len(content) != 0:
        cmdName = content.splitlines()[0]
        content = content[len(cmdName)+1:]
        code = ""
        for i in content.split("\n"):
            if(i.startswith("endofProtCode")):
                break
            code += i + "\r\n"
        code = code[:-2]
        content = content[content.find('endofProtCode'):]
        content = content[len('endofProtCode')+1:]
        KeyCheck = content.splitlines()[0]
        content = content[len(KeyCheck)+1:]
        CheckIt = content.splitlines()[0]
        content = content[len(CheckIt)+1:]
        
        #todo clean up 
        #print(cmdName)
        if cmdName == "exec":
            data.append(0x48)
        elif cmdName == "eval":
            data.append( 9)
        elif cmdName == "read":
            data.append( 3)
        if cmdName == "execs":
            data.append( 0x48 | 0x80)
        elif cmdName == "evals":
            data.append( 9 | 0x80)
        elif cmdName == "reads": 
            data.append( 3 | 0x80)
        #print(code)
        data += code.encode("ASCII")
        data.append(0)
        if CheckIt == "Check":
            m.update(KeyCheck.encode("ASCII") + b'\0')
            data.append(0)
        else:
            data.append(1)
    flags = 0
    if flagsRaw == "Encry":
        flags |= 1
    return (m.digest(),data,flags | 2)

def MakeFild(size,currentPos,dataKey,name,flags):
    global entries
    feld1 = size.to_bytes(8, 'little')
    feld2 = currentPos.to_bytes(8, 'little')
    feld3 = flags.to_bytes(8, 'little')
    resByte = feld1 + feld2 + feld3 + b'\0' * 8 + dataKey
    #print(name.encode('ASCII'),":".join("{:02x}".format(ord(c)) for c in name),size)
    
    #encrypt
    
    if isinstance(name, bytes):
        key1 = name
    else:
        m = hashlib.sha256()
        m.update(name.encode('ASCII'))
        key1 = m.digest()
    print("Key1: " + key1.hex())
    m = hashlib.sha256()
    m.update(key1)
    key2 = m.digest()
    print("Key2: " + key2.hex())
    cipher = AES.new( key1, AES.MODE_CBC, iv )
    resByte = cipher.encrypt( resByte )

    fhead.write("unsigned char PICDAT" + (str)(entries) + "[64] = {")
    j = 0
    for i in resByte:
        fhead.write((str)(i))
        if j != 63:
            fhead.write(",")
        j = j + 1
    fhead.write("};\r\n")
    
    fhead.write("unsigned char PICID" + (str)(entries) + "[32] = {")
    j = 0
    for i in key2:
        fhead.write((str)(i))
        if j != 31:
            fhead.write(",")
        j = j + 1
    fhead.write("};\r\n")
    entries += 1

def genWithName(name,data,dataKey,flags):
    global currentPos
    sizeR = len(data)
    size = (int)(((int)((sizeR + 31) / 32)) * 32)
    
    MakeFild(sizeR,currentPos,dataKey,name,flags)   
    
    data = data + b'\0' * (size - sizeR)
    #print((str)(size),(str)(sizeR))
    cipher = AES.new( dataKey, AES.MODE_CBC, iv )
    resDataByte = cipher.encrypt( data )
    fdata.write(resDataByte)

    
    #alt entire
    if isinstance(name, str) and name.startswith("images"): #tut says only jpg and png but it realy is all
        name = name.split("\\")[-1]
        name = name.lower()
        MakeFild(sizeR,currentPos,dataKey,name,flags) #with ending
        name = name[:name.rindex('.')]
        MakeFild(sizeR,currentPos,dataKey,name,flags) #without ending
        
    
    print("dataKey: " + dataKey.hex() + "\n")
    currentPos = currentPos + size

    
    
for i in all_files:
    name = i[len(sys.argv[1]):]
    print(name)
    dataKey = get_random_bytes(32)
    pat = getProtectFile(name,dataKey)
    flags = 0
    if pat != None:
        flags = pat[2]
        f=open("inst.bin", "wb")
        f.write(pat[1])
        f.close()
        genWithName(name,pat[1],dataKey,flags)
        name = pat[0]
        dataKey = get_random_bytes(32)
    flags = flags & ~0x2
    f=open(i,"rb")
    data=f.read()
    f.close()
    genWithName(name,data,dataKey,flags)

fhead.write("#define NUMPIC " + (str)(entries) + "\r\n")

j = 0
fhead.write("unsigned char *PICDATA[] = {")
for i in range(entries):
    fhead.write("PICDAT" + (str)(i))
    if j != entries - 1:
        fhead.write(",")
        j = j + 1
fhead.write("};\r\n")

j = 0
fhead.write("unsigned char *PICID[] = {")
for i in range(entries):
    fhead.write("PICID" + (str)(i))
    if j != entries - 1:
        fhead.write(",")
        j = j + 1
fhead.write("};\r\n")

fdata.close()
fhead.close()
