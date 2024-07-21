import time
import os

respath = r'resources'
if not os.path.exists(respath):
    os.makedirs(respath)

#Parse MAME source
def return_ROMNAME(string):
    name = bytes(string, 'utf-8')
#remove ROM_START
    name = name[11:]
    for k in range(0,len(name),1):
        if name[k] == 0x20: #When parsing a Space
            return str(name[:k].decode('iso-8859-1'))
        
def return_OKI_SIZE(text):
    x = 0 #The size of the ROM is the second HEX value, so track how many xs we read
    for i in range(0,len(text),1):
        if chr(text[i]) == "x":
            x += 1
            if x == 2:
                return text[i-1:i+6]
            
def return_OKI_NAMES(text):
    points = {}
    x = 0 #Track how many " we've read to grab the whole string
    for i in range(0,len(text),1):
#        if chr(text[i]) == ":
#        print(text[i])
#        time.sleep(30)
        if text[i] == 0x22: #HEX of "
            points.update({x : i})
            x += 1
            if x == 2:
                return text[points[0]:points[1]+1]


def return_OKI_LOAD(text):
    payload = {}
    sizes = {}
    for i in range(0,len(text),1):
        if "ROM_LOAD" in text[i]:
            name = bytes(text[i][11:], 'utf-8') #Remove first 12 Bytes of string
            payload.update({i : str(return_OKI_NAMES(name).decode('iso-8859-1'))})
            sizes.update({i : str(return_OKI_SIZE(name).decode('iso-8859-1'))})
#            for k in range(0,len(name),1):
#                print(chr(name[k]))
#                if chr(name[k]) == ",":
#                    temp = return_OKI_NAME(name[k:])
#                    payload.update({i : str(name[:k].decode('iso-8859-1'))})
#                    temp = return_OKI_SIZE(name[k:])
#                    sizes.update({i : str(return_OKI_SIZE(name[k:]).decode('iso-8859-1'))})
#                    ROM["OK_SZ"].update({i : str(name[k+11:k+18].decode('iso-8859-1'))})
#                    break
#    print(payload)
    return payload, sizes
#            name = name[8:] #Remove first 8 Bytes of string

def parse_ROM_def(text):
    data = {}
    line_no = 0
    for line in text:
        line_no += 1
        if "oki" in line: #See how many OKI ROMs are defined2
            data = return_OKI_LOAD(text[line_no:line_no+2])
    return data 
    
def parse_MAME_CPS1_SRC():
    with open("capcom-cps1.cpp", "r") as file:
        file_contents = file.readlines()
#        print(file_contents[14430])
#        time.sleep(30)
    line_no = 0 #Used to keep track of Lines
    valid = 0
    ROM = {}
    OKI = {}
    ROM.update({"no" : 0, "name" : {},"start" : {},"end" : {},"OKI" : {},"OK_SZ" : {}})
    for line in file_contents:
        line_no += 1
        if "ROM_START" in line: #Only return stuff related to ROM Definitions
            ROM["start"].update({ROM["no"]  : line_no})
            ROM["name"].update({ROM["no"] : return_ROMNAME(line)})
        if "ROM_END" in line:
            ROM["end"].update({ROM["no"]  : line_no})
    #Parse the Line and return useful values
            OKI = parse_ROM_def(file_contents[ROM["start"][ROM["no"]]:ROM["end"][ROM["no"]]])
            if len(OKI): #Only appoend valid data
                ROM["OKI"].update({ROM["no"] : OKI[0]})
                ROM["OK_SZ"].update({ROM["no"] : OKI[1]})
    #            ROM["OKI"].update({ROM["no"] : parse_ROM_def(file_contents[ROM["start"][ROM["no"]]:ROM["end"][ROM["no"]]])})
    #            ROM["def"].update({ROM["no"]  : file_contents[line_no - ROM["start"][ROM["no"]]]})
                ROM["no"] += 1
        if "cps_state" in line and len(ROM["start"]): #We've stopped reading
            return ROM
#    return ROM
#                print((return_ROMNAME(line)),line_no)

ROM = parse_MAME_CPS1_SRC()
print("NUM OF ROMS - ", len(ROM["name"]))
print("NUM OF OKI - ", len(ROM["OKI"]))
#time.sleep(30)
#Outout the Resource files
for i in range(0,ROM["no"],1):
    if len(ROM["OKI"][i]): #Only do this with valid ROMs
        path = os.path.join(respath,ROM["name"][i])+".py"
#        print(ROM["name"][i],ROM["OKI"][i])
        with open(path, "w") as out:
            out_str = str("#{}\n{}").format(ROM["name"][i],"OKI_NAMES = [")
            out_str_sz = "OKI_SIZES = [" #At the same time, work on the Sizes table var
            for k in range(0,len(ROM["OKI"][i]),1): #Fill table with OKI names
                out_str += ROM["OKI"][i][k]
                out_str_sz += ROM["OK_SZ"][i][k]
                if k+1 == len(ROM["OKI"][i]):
                    out_str += "]"
                    out_str_sz += "]"
                    out_str += str("\n{}").format(out_str_sz)
                else:
                    out_str += ","
                    out_str_sz += ","
            print(out_str)
#            time.sleep(2)
            out.write(out_str)

