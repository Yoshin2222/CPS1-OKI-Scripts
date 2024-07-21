import os
import sys
import importlib

#Generate folders if they don't already exist
rompath = r'roms'
if not os.path.exists(rompath):
    os.makedirs(rompath)
respath = r'resources'
if not os.path.exists(respath):
    os.makedirs(respath)

print("----- YOSHINS OKI ROM SAMPLE EXTRACTOR ------")
print("Enter name of OKI ROM to extract Samples from...")
game_name = input().lower()
#Invalid Input: No Resource file
while not os.path.exists(os.path.join(respath, game_name+".py")):
    print("GAME NOT SUPPORTED! Look in resources")
    game_name = input("Try something else: ")    

#Grab the needed resource file
sys.path.append(respath)
res = importlib.import_module(game_name.lower()) #Ensure lowercase for ease of input



#Once a file is loaded, grab important data before extracting
#file_size = os.path.getsize(input_path)

#Create a temporary copy of the total OKI data
OKI_ROM = bytearray()
for i in range(0,len(res.OKI_NAMES),1):
#    path = str("{}{}").format(rompath,res.OKI_NAMES[i])
    path = os.path.join(rompath,game_name,res.OKI_NAMES[i])
    with open(path, "rb") as input:
        OKI_ROM += input.read(os.path.getsize(path))

sample_pointer_section = 0x400
sp_cursor_start = 8 #Skip the first 8 bytes as they're always blank
sample_pointer_cursor = sp_cursor_start
sample_start_pointers = {} #Keep a list of where every sample begins in ROM
sample_end_pointers = {} #Keep a list of where every sample ends in ROM

#Gather Pointer data
for index in range(0,sample_pointer_section,8):
    if int.from_bytes(OKI_ROM[sample_pointer_cursor:sample_pointer_cursor+8],"big") != 0xFFFFFFFFFFFFFFFF: #Invalid
        #First grab Start Pointer (first 3 Bytes since the OKI uses 24-bit addresses
        pointer = int.from_bytes(OKI_ROM[sample_pointer_cursor:sample_pointer_cursor+3],"big")
        sample_start_pointers.update({index>>3 : pointer})
        sample_pointer_cursor += 3
        #Grab End Pointer
        pointer = int.from_bytes(OKI_ROM[sample_pointer_cursor:sample_pointer_cursor+3],"big")
        sample_end_pointers.update({index>>3 : pointer})
        sample_pointer_cursor += 5 #Move to the next Pointer
#print(sample_start_pointers)

#With this pointer data, isolate each Sample, and write it to a new folder!
sample_path = os.path.join("OKI_OUT",game_name)
while not os.path.exists(sample_path):
    os.makedirs(sample_path)
sample_data = {}

for i in range(0,len(sample_start_pointers),1):
        if len(OKI_ROM[sample_start_pointers[i]:sample_end_pointers[i]]) != 0: #Ensure not invalid
            smp = str("{} - {} - {}-{} = {}-{}").format(game_name,"SMPL", i,hex(i),hex(sample_start_pointers[i]),hex(sample_end_pointers[i]))
            sample_data.update({i : OKI_ROM[sample_start_pointers[i]:sample_end_pointers[i]]})
            with open(os.path.join(sample_path, smp),"wb") as out:
                out.write(bytes(sample_data[i]))

