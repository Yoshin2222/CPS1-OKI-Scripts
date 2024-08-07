import os
import os, glob
import time
import sys
import importlib

start_time = time.time()

audio_inp_format = ".wav" #Format of choice, defaults to wav
wav_header_length = 0x28
rompath = r'roms'
if not os.path.exists(rompath):
    print("Creating Roms path...")
    os.makedirs(rompath)
respath = r'resources'
if not os.path.exists(respath):
    os.makedirs(respath)


print("------------ YOSHINS OKI COMPILER ------------")

print("Enter the name of the game you want to compile OKI ROMs for...")
game_name = input().lower()
#Invalid Input: No Resource file
while not os.path.exists(os.path.join(respath, game_name+".py")):
    print("GAME NOT SUPPORTED! Look in resources")
    game_name = input("Try something else: ")    

COMP_OKI_PATH = "COMPILED_OKI"
input_path  = "input_wav"
output_path = "compressed_wav"
input_path = os.path.join(COMP_OKI_PATH,input_path,game_name)

if not os.path.exists(input_path):
    msg = str("No WAVs to compress! Ensure there's a folder named -{}- containing - ".format(input_path))
    msg += "\n16-Bit Signed, 7575hz PCM.WAV files\n"
    msg += "I'll go make it right quick, now go put stuff in it!\n"
    msg += "Press Enter to exit..."
    os.makedirs(input_path)
    input(msg)
    quit()

output_path = os.path.join(COMP_OKI_PATH,output_path,game_name)

if not os.path.exists(output_path):
    print("Creating Output path...")
    os.makedirs(output_path)


def evaluate_input_wavs():
    names = {}
    index = 0
    print("======== INPUT WAV FILES ========")
    for filename in glob.glob(os.path.join(input_path, '*.wav')):
        path = os.path.join(os.getcwd(), filename)
        outpath = filename.replace(input_path,output_path,1)
        with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
            print(filename,"\t - SIZE = ", os.path.getsize(filename),"  = ", hex(os.path.getsize(filename))," bytes")
            names.update({index : filename})
            index += 1
    return names

def return_outnames():
    out_names = {}
    index = 0
    for i in range(0,len(pcmnames),1):
        outpath = pcmnames[i].replace(input_path,output_path,1)
        out_names.update({index : outpath})
        index += 1
    return out_names

#-------------------- FUNCTIONS --------------------
def return_pcm_name(name):
    pcmname = (name + audio_inp_format).lower()
    return pcmname

def close_program(msg,name,val):
    print(name, " - isn't formatted properly")
    string = str("{} - {}").format(msg,hex(val))
    sys.exit(string)

def to_array16(table):
    cursor = 0
    array = bytearray(len(table))
    while cursor < len(table)-3:
        WORD = int.from_bytes(table[cursor:cursor+2], byteorder='little')
        array[cursor:cursor+2] = WORD.to_bytes(2,"big")
        cursor += 2
    return array


#In order to properly compress, we need to ensure the format of the WAV file matches certain parameters
def format_PCM(table,name):
    cursor = 0
    debug = 0
    # Parse Header
    ChunkID = int.from_bytes(table[cursor:cursor+4], byteorder='big')
    if ChunkID != 0x52494646: #Hex representation of "RIFF"
        close_program("ERROR 1: No RIFF Identifier",name,ChunkID)
    if debug == 1:
        print("VALID 'RIFF' - \t\t\t", hex(ChunkID))
    cursor += 4

    ChunkSize = int.from_bytes(table[cursor:cursor+4], byteorder='little')
    if ChunkSize != len(table) - 8:
        close_program("ERROR 2: Invalid ChunkSize",name,ChunkSize)
    if debug == 1:
        print("VALID CHUNKSIZE - \t\t", hex(ChunkSize))
    cursor += 4

    Format = int.from_bytes(table[cursor:cursor+4], byteorder='big')
    if Format != 0X57415645: #Hex representation of "WAVE"
        close_program("ERROR 3: Bad WAVE Format",name,Format)
    if debug == 1:
        print("VALID WAVE FORMAT - \t\t", hex(Format))
    cursor += 4

    #Now parse "fmt" chunk
    data = table[cursor:len(table)]
    cursor = 0

    Subchunk1ID = int.from_bytes(data[cursor:cursor+4], byteorder='big')
    if Subchunk1ID != 0x666D7420: #Hex representation of "fmt "
        close_program("ERROR 4: Invalid Subchunk FMT",name,Subchunk1ID)
    if debug == 1:
        print("VALID SUBCHUNK ID FORMAT - \t", hex(Subchunk1ID))
    cursor += 4

    Subchunk1Size = int.from_bytes(data[cursor:cursor+4], byteorder='little')
    if Subchunk1Size != 0x00000010:
        close_program("ERROR 5: Invalid Subchunk Size",name, Subchunk1Size)
    if debug == 1:
        print("VALID SUBCHUNK SIZE - \t\t", hex(Subchunk1Size))
    cursor += 4

    AudioFormat = int.from_bytes(data[cursor:cursor+2], byteorder='little')
    if AudioFormat != 0x00000001:
        close_program("ERROR 6: Invalid Audio Format",name, AudioFormat)
    if debug == 1:
        print("VALID AUDIO FORMAT - \t\t", hex(AudioFormat))
    cursor += 2

    NumChannels  = int.from_bytes(data[cursor:cursor+2], byteorder='little')
    if NumChannels != 0x00000001:
        close_program("ERROR 6-2: Invalid Number of channels ",name, NumChannels)
    if debug == 1:
        print("VALID # OF CHANNELS- \t\t", hex(NumChannels))
    cursor += 2

    SampleRate = int.from_bytes(data[cursor:cursor+4], byteorder='little')
    if SampleRate != 7575:
        close_program("ERROR 8: Invalid Sample Rate",name, SampleRate)
    if debug == 1:
        print("VALID SAMPLE RATE - \t\t", SampleRate)
        
    cursor += 4

    ByteRate = int.from_bytes(data[cursor:cursor+4], byteorder='little')
    cursor += 4
    BlockAlign = int.from_bytes(data[cursor:cursor+2], byteorder='little')
    cursor += 2

    BitsPerSample = int.from_bytes(data[cursor:cursor+2], byteorder='little')
    if BitsPerSample != 0X00000010:
        close_program("ERROR 9: Unexpected Bits per Sample",name, BitsPerSample)
    if debug == 1:
        print("VALID BITS PER SAMPLE - \t", hex(BitsPerSample))

    cursor += 2

    data = data[cursor:len(data)]
    cursor = 0

    chunkName = int.from_bytes(data[cursor:cursor+4], byteorder='big')
    if chunkName != 0x64617461: #Hex representation of "data"
        cursor += 0x2C #Ignore SMPL Data   
        chunkName = int.from_bytes(data[cursor:cursor+4], byteorder='big')
        if chunkName != 0x64617461: #Hex representation of "data"
            close_program("ERROR 10: Invalid Chunkname",name,chunkName)
    if debug == 1:
        print("VALID CHUNKNAME - \t\t", hex(chunkName))
    cursor += 4

    datalength = int.from_bytes(data[cursor:cursor+4], byteorder='little')
    cursor += 4
    payload = data[cursor+4:len(data)]
    cursor = 0
#OPTIMIZE PAYLOAD BY TIGHTENING IT TO ACTUAL DATA
    while payload[cursor] == 0:
        cursor += 1
    payload = payload[cursor:len(payload)]
    cursor = 0
#SCAN PAYLOAD FOR 0x00000000, assume this is silence and thus the real end of sound data
    while cursor+4 < len(payload):        
        if int.from_bytes(payload[cursor:cursor+4], byteorder='little') == 0x00000000:
            if int.from_bytes(payload[cursor+4:cursor+8], byteorder='little') == 0x00000000:
                payload = payload[:cursor]
                cursor += len(payload) #break out of loop
            else:
                cursor += 4
        else:
            cursor += 4

    if debug == 1:
        print("PAYLOAD - ",payload[0:8]," - ",payload[0:8])
        print("TABLE - ",len(table)," - ",table[0:8])
        print("DATA - ",len(data)," - ",data[0:8])
        print("PAYLOAD - ",len(payload)," - ",payload[0:8])
        time.sleep(2)

    #Repeat last byte if needed to ensure an Even number of bytes
    if len(payload)%2 == 1:
        payload.append(payload,payload[len(payload -1)])

    wav_data = to_array16(payload)
    if len(wav_data)&2 != 0:
        wav_data = wav_data[0:len(wav_data)-1]

    return wav_data

#Based on the work found here https://www.cs.columbia.edu/~hgs/audio/dvi/
#indextable = [-1,-1,-1,-1,2,4,6,8,-1,-1,-1,-1,2,4,6,8]
#stepsizetable = [7,8,9,10,11,12,13,14,16,17,19,21,23,25,28,31,34,37,41,45,50,55,60,66,73,80,88,97,107,118,130,145,157,173,190,209,230,253,279,307,337,371,408,449,494,544,598,658,724,796,876,963,1060,1166,1282,1411,1552,1707,1878,2066,2272,2499,2749,3024, 3327,3660,4026,4428,4871,5358,5894,6484,7132,7845,8630,9493,10442,11487,12635,13899,15289,16818,18500,20350,22385,24623,27086,29794,32767]
indextable = [-1,-1,-1,-1,2,4,6,8,-1,-1,-1,-1,2,4,6,8]
#indextable = [-1,-1,-1,-1,2,4,6,8]
stepsizetable = [16, 17, 19, 21, 23, 25, 28, 31, 34, 37,41, 45, 50, 55, 60, 66, 73, 80, 88, 97,107, 118, 130, 143, 157, 173, 190, 209, 230, 253,279, 307, 337, 371, 408, 449, 494, 544, 598, 658,724, 796, 876, 963, 1060, 1166, 1282, 1411, 1552]
def compress_sample(table,name):
    length = len(table)
    predicted_sample = 0
    index = 0
    msb = 0
    lsb = 0
    stepsize = stepsizetable[0]
#    stepsize = int.from_bytes(table[0:2], byteorder='big',signed = "false")
#    stepsize = 0x0C00 #stepsizetable[(len(stepsizetable)>>1)-1]
    newsample = 0
    difference = 0
    finalsample = 0
    final_index = 0
    newtable = bytearray(length>>2)
    print("Now compressing file...",name)
#    i = itertools.count(start = 0, step = 2)
    #Go through the whole file
    for i in range(0,length,2):
        #First, snag 16-Bit Sample from Source file
        original_sample = int.from_bytes(table[i:i+2], byteorder='big',signed = "false")
#        original_sample += (0x10000>>1)#-(0x10000>>2) #(stepsizetable[len(stepsizetable)-1])-1
#        original_sample += (stepsizetable[len(stepsizetable)-1])
#        if (i&2) == 0:
#            original_sample ^= 0b1000000000000000
#        else:
#            original_sample ^= 0b1000000000000000


        original_sample >>= 3 #Algo uses 12-bit Input

        difference = original_sample - predicted_sample #Find difference from predicted sample
        if difference >= 0: #Set Sign Bit and find absolute value of difference
            newsample = 0
        else: 
            newsample = 8
            difference = -difference
        mask = 4
        tempstepsize = stepsize
        for k in range(0,3,1):
            if (difference >= tempstepsize):
                newsample |= mask
                difference -= tempstepsize
            tempstepsize >>= 1
            mask >>= 1
        #Store 4-Bit Newsample
        if (i & 2):
            finalsample = 0
            msb = msb << 4
            lsb = newsample &0x0f
            finalsample ^= msb + lsb
#            finalsample = finalsample << 4
#            finalsample += newsample
            newtable[final_index] = finalsample
#            print("Final Byte = ", hex(finalsample)," - ", bin(finalsample))
            final_index += 1
        else:
            msb = newsample&0x0f

        #Compute New_Sample estimate using predicted_Sample
        difference = 0
        if (newsample & 4):
            difference += stepsize
        if (newsample & 2):
            difference += stepsize>>1
        if (newsample & 1):
            difference += stepsize>>2
        difference += stepsize>>3
        if (newsample & 8):
            difference = -difference

        predicted_sample += difference
        if (predicted_sample > stepsizetable[len(stepsizetable)-1]):
            predicted_sample = stepsizetable[len(stepsizetable)-1]
        elif (predicted_sample < -stepsizetable[len(stepsizetable)-1]-1):
            predicted_sample = -stepsizetable[len(stepsizetable)-1]-1

        #Compute new Stepsize
        index += indextable[newsample]
#        index += indextable[newsample & 0x07]
        if (index < 0):
            index = 0
        elif (index > len(stepsizetable)-1):
            index = len(stepsizetable)-1
#        print("INDEX - ", index)
        stepsize = stepsizetable[index]

    print("COMPRESSED LENGTH = ", hex(len(newtable)), " - ", len(newtable), " Bytes")
    return newtable


#-------------------- PARSE INPUT --------------------
pcmnames = evaluate_input_wavs()
out_names = return_outnames()
#Keep important information for when we generate an OKI Sample ROM
compressed_data = {}
compressed_lengths = {}
compressed_offsets = {}
#compressed_data: list[int]
#compressed_lengths: list[int]
#compressed_offsets: list[int]
for i in range(0,len(pcmnames),1):
    compressed_data.update({i : {}})
    compressed_lengths.update({i : 0})
    compressed_offsets.update({i : 0})

#print("PCNAMES")
#print(pcmnames)
time.sleep(0.4)


#-------------------- COMPRESS DATA --------------------
for z in range(0,len(pcmnames),1):
    with open(pcmnames[z], "rb") as input:
        size = os.path.getsize(pcmnames[z])
        tempfile = bytearray()
        tempfile = input.read(size)
        tempfile2 = bytearray(size)
        adpcm = bytearray(size)
        print(pcmnames[z], " - Size = ", hex(size), " - ", size, " Bytes")
        pcm_data = format_PCM(tempfile,pcmnames[z])
        compressed_data[z] = compress_sample(pcm_data,pcmnames[z])

    #Write the flipped data to a new file
    with open(out_names[z], "wb") as out:
#        print("Writing - ", out_names[z], " -")
        out.write(bytes(compressed_data[z]))
#        print("FINISHED COMPRESSING - ", pcmnames[z])


#-------------------- GENERATE AN OKI ROM BASED ON COMPRESSED DATA --------------------
print("Now writing OKI ROM...")

#Grab the needed resource file
sys.path.append(respath)
res = importlib.import_module(game_name.lower()) #Ensure lowercase for ease of input

#OKI_NAME = "sf2_18.11c" #Named after the one used by SF2 for testing purposes
OKI_LENGTH = sum(res.OKI_SIZES)
OKI_Pointer_section_length = 0x400 #Data set aside for Pointer data, actual Sample data starts after this
#OKI_ROM = bytearray(OKI_LENGTH)
OKI_ROM = bytearray([0xff]*OKI_LENGTH)
OKI_ROM[0:8] = 0x0000000000000000.to_bytes(8,"big") #Ensures first Pointers are blank

sample_pointer_start = OKI_Pointer_section_length #Value containing Pointer to Sample data
sample_pointer_end = 0
sample_pointer_curosr = 8 #Starts at 8 so the first Sample is left blank
sample_data_curosr = sample_pointer_start

for i in range(0,len(pcmnames),1):
    #Sample data is fairly straightforwsrd, comprising of 2 empty Bytes, and 3 bytes apiece
    #denoting the Start and Endpoint of a given sample respectively
#Write Sample Pointers to ROM
#Write Start Pointer
    OKI_ROM[sample_pointer_curosr:sample_pointer_curosr+3] = sample_pointer_start.to_bytes(3,"big")
    sample_pointer_end = sample_pointer_start+ len(compressed_data[i]) #Ensures ending Pointer never overlaps
    sample_pointer_start = sample_pointer_end+1  #Ensure no data overlap
#Write End Pointer
    sample_pointer_curosr += 3
    OKI_ROM[sample_pointer_curosr:sample_pointer_curosr+3] = sample_pointer_end.to_bytes(3,"big")
    sample_pointer_curosr += 3
    OKI_ROM[sample_pointer_curosr:sample_pointer_curosr+2] = 0x0000.to_bytes(2,"big") #Set ramaining bytes to 0x00
    sample_pointer_curosr += 2 #Last 2 bytes are empty so ignore them

#Write Sample data to ROM
    OKI_ROM[sample_data_curosr:sample_data_curosr+ len(compressed_data[i])] = compressed_data[i]
    sample_data_curosr += len(compressed_data[i])
#    print(OKI_ROM)

#Pad the rest of Pointer data with 0xFF
#if sample_pointer_curosr < OKI_Pointer_section_length:
#    remainder = OKI_Pointer_section_length-sample_pointer_curosr
#    for i in range(sample_pointer_curosr,OKI_Pointer_section_length,4):
#        OKI_ROM[i:i+4] = 0xFFFFFFFF.to_bytes(4,"big")

#Write the output ROMs
cursor = 0
index = 0
comp_path = r'COMPILED_OKI'
for name in res.OKI_NAMES:
    path = os.path.join(comp_path,rompath,game_name)
    if not os.path.exists(path):
        print("Creating Compiled path...")
        os.makedirs(path)
    with open(os.path.join(path,name),"wb") as out:
        msg = str("Writing {}").format(os.path.join(path,name))
        out.write(bytes(OKI_ROM[cursor:cursor+res.OKI_SIZES[index]]))
        cursor += res.OKI_SIZES[index]
        index += 1

totalspace = 0
outinfo = "- OKI ROM INFO -\n"
#Display Sample info
for i in range(0,len(pcmnames),1):
    printname = pcmnames[i].replace(input_path,"- ",1)
    printstr = str("{}\t - {} - {} - bytes ").format(printname,hex(len(compressed_data[i])),len(compressed_data[i]))
    totalspace += len(compressed_data[i])
    print(printstr)
    outinfo += printstr + "\n"
remainder = OKI_LENGTH-totalspace
outinfo += "\n"
printstr = str("TOTAL SPACE USED = {} of {} - {}/{} - {}/{} bytes remaining").format(totalspace,OKI_LENGTH,hex(totalspace),hex(OKI_LENGTH),hex(remainder),remainder)
outinfo += printstr + "\n"
print(printstr)
printstr = str("TOTAL SAMPLES USED = {} of {}").format(len(pcmnames),(OKI_Pointer_section_length>>2)-1)
print(printstr)
outinfo += printstr + "\n"

info_name = "OKI_ROM_INFO.txt"
with open(info_name,"w") as out:
    out.write(outinfo)

print("TIME TO EXECUTE - ",time.time()-start_time)
time.sleep(3)
