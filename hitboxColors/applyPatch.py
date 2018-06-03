import os
import sys
import json
import argparse

try:
    import gciso
except ImportError:
    gciso = None

parser = argparse.ArgumentParser(description="Apply patch data to .dat file or .iso file.")
parser.add_argument("patchfile", help="The patch json file.")
parser.add_argument("targetfile", help="The .dat/.iso file to apply the patch to.")
args = parser.parse_args()

with open(args.patchfile) as f:
    patchData = json.load(f)

if args.targetfile.lower().endswith(".iso"):
    if not gciso:
        quit("The gciso module must be installed to patch .iso files!")
    with gciso.IsoFile(args.targetfile) as isoFile:
        for file in patchData:
            filePatch = patchData[file]
            for i in range(0, len(filePatch), 2):
                offset, data = filePatch[i+0], filePatch[i+1]
                data = bytes.fromhex(data)
                isoFile.writeFile(file.encode("ascii"), offset, data)
elif args.targetfile.lower().endswith(".dat"):
    fileBase = os.path.basename(args.targetfile)
    if fileBase not in patchData:
        quit("No patch data for '{}'!".format(fileBase))
    filePatch = patchData[fileBase]
    with open(args.targetfile, "r+b") as f:
        for i in range(0, len(filePatch), 2):
            offset, data = filePatch[i+0], filePatch[i+1]
            data = bytes.fromhex(data)
            f.seek(offset)
            f.write(data)
else:
    quit("File must either be a .dat or a .iso file!")
