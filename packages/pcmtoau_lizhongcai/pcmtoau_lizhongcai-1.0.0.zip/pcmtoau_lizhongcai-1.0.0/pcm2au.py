import sys
import struct
import os

if len(sys.argv) != 2:
    print ("Usage: 'python pcm2au.py <Source PCM File>'")
    sys.exit(1)
srcFilename = sys.argv[1]
dstFilename = '%s.au' % os.path.splitext(srcFilename)[0]
with open(srcFilename, 'r+b') as srcFile, open(dstFilename, 'w+b') as dstFile:
    ###################################
    # Write the AU header
    ###################################
    dstFile.write(b'.snd')
    dstFile.write(struct.pack('BBBB', 0,0,0,24))
    dstFile.write(struct.pack('BBBB', 0xff,0xff,0xff,0xff))
    dstFile.write(struct.pack('BBBB', 0,0,0,3))
    dstFile.write(struct.pack('BBBB', 0,0,0x1f,0x40))
    dstFile.write(struct.pack('BBBB', 0,0,0,1))

    #############################
    # swap the PCM samples
    #############################
    while True:
        data = srcFile.read(2)
        if len(data) == 2:
            word = struct.unpack('<H', data)[0]
            dstFile.write(struct.pack('>H', word))
        else:
            break
        
