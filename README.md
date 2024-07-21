Python Scripts designed to Extract/compile Samples to and from CPS1 games. Simply add the unzipped
game to roms, generate resources if ya haven't already and have fun!
Script made with Python 3.10.6

- GENERATE RESOURCES
The script reads capcom-cps1.cpp and isolates every game, outputting a resource file for every
compatible game containing the names of every OKI ROM as well as their sizes

- OKI_EXTRACTOR
The first 0x400 bytes of OKI data are reserved for pointers to each sample, the first 8 bytes always being
0x00. Pointers are laid out like this
  xxxyyy00
  xxx - Start Point of Sample data (24-bit)
  yyy - Start Point of Sample data (24-bit)
This data is included in the names of each sample. Resource files are required to read the names of each OKI ROM in roms/(game)

- GENERATE_OKI_ROM
Takes every Sample in COMPILED_OKI/input_wav/(game), compresses them to 4-bit VOX ADPCM, and generates OKI ROMs with it.
These files can simply be inserted into a given CPS1 game, and the script outputs these compressed version individually in
COMPILED_OKI/compressed_wav/(game). Resource files are required for when compiling ROMs in the case there are none in roms
