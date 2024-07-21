# CPS1-OKI-Generator
Python Script meant to convert .wav files to a CPS1 OKI (Samples) ROM

As simple as it's gonna get! A Python script designed to import 16-bit Signed PCM 7575 hz wav files in a folder named input_wav, and spits out an OKI ROM readable by the CPS1, pointers and compression and all! Only thing is the compression doesn't seem to be perfect as there's oftentimes clicking present, btu I think it's usable enough to share and get more eyes on

Inspired by the work of Fabian Sangliard, writer of the Book of CP System and the creator of CCPS (CPS1 SDK)
https://github.com/fabiensanglard/ccps/blob/master/oki/adpcm.go

1.03) This is a big one! Alongside the Generator Script, created 2 sister scripts, 1 for extracting OKI Samples from CPS1 Games, and one for generating needed data by reading MAMEs
capcom-cps1.cpp source code. This wey ya can simply rescan the source should new games be added
Alongside this, the script now uses individual ROM Folders for when compiling WAV files to a usable OKI ROM (for instance, SF2 relies on WAVs in COMPILED_OKI/input_wav/sf2 when creating OKI ROMs, and outputs them to COMPILED_OKI/roms/sf2)
Simply run the Generate Resources script, and either add unzipped games to roms to extract samples, or run generate_OKI twice if ya like, once to generate the output folder, the other to compile whatever is in input_wav!

1.021) Removed some time.sleep() stuff (was there for devugging purposes) so the script runs MUCH faster now. For reference, compressing 7 samples took 10 seconds. The script csn now compress 96 of em in 4

1.02) Improved ADPCM Compression, and at the behest of a user on the Chiptune Cafe, added an OKI ROM Sample extractor! Simply enter the name of the OKI ROM ya want to extract samples from, and it will generate each one in a new folder, including the SAtart/End pointers in their names for convenience! Simply open any given sample in Audacity as VOX ADPCM 7575 HZ No Endian Mono sounds and ya should be good!
