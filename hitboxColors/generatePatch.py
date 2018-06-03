import os
import sys
import json
import argparse

# this returns the same hash for hitboxes that are "functionally equivalent"
# i.e. have the same post-hit effect and hit the same targets
def hitboxHash(hitbox):
    fields = ["damage", "angle", "kbGrowth", "weightDepKb", "hitboxInteraction",
        "baseKb", "element", "shieldDamage", "hitGrounded", "hitAirborne"]
    return ",".join(str(hitbox[field]) for field in fields)

def getPatch(datJsonFile, disableGrabs, zeroGravity):
    with open(datJsonFile) as f:
        data = json.load(f)

    patch = []
    maxGuid = 0
    dataOffset = 0x20
    for i, subaction in enumerate(data["nodes"][0]["data"]["subactions"]):
        eventStrOffset = dataOffset + subaction["eventsOffset"]
        hitboxes = {}
        activeHitboxes = {}
        eventOffset = eventStrOffset
        for event in subaction["events"]:
            hitbox = None

            if "name" in event and event["name"] == "hitbox":
                hitbox = event["fields"]
                activeHitboxes[event["fields"]["id"]] = hitbox

                if disableGrabs and event["fields"]["element"] == "grab":
                    # the byte @ 17 has this layout: BEEEEEXS
                    # where B belongs to base knockback, E to element, X is unknown, S to shield damage
                    offset = eventOffset + 17
                    originalValue = bytes.fromhex(event["bytes"])[17]
                    # we want to zero out the element bits to make it 'normal'
                    patch.append((offset, bytes([0b10000011 & originalValue])))

            if "name" in event and event["name"] == "adjustHitboxDamage":
                hitboxId = event["fields"]["hitboxId"]
                if hitboxId in activeHitboxes:
                    hitbox = activeHitboxes[hitboxId].copy()
                    hitbox["damage"] = event["fields"]["damage"]

            if hitbox:
                hbHash = hitboxHash(hitbox)
                if hbHash in hitboxes:
                    hitboxGuid = hitboxes[hbHash]
                else:
                    hitboxGuid = len(hitboxes)
                    hitboxes[hbHash] = hitboxGuid

                # for hitbox: we are skipping the first bit of the damage field here
                # we don't want to set it anyways, but we also have to hope it's never 1
                # for the adjustHitboxDamage event: the damage is in the last byte (+3 too)
                damageOffset = eventOffset + 3

                if hitboxGuid > maxGuid:
                    maxGuid = hitboxGuid
                    #print("{} {}: {}".format(hex(i), subaction["name"], hitboxGuid))

                assert damageOffset < 0xffff
                assert hitboxGuid < 0xff
                patch.append((damageOffset, bytes([hitboxGuid])))

            eventOffset += event["length"]

    print(maxGuid)

    if zeroGravity:
        gravityOffset = 0x17 * 4
        fullAttributesOffset = dataOffset + data["nodes"][0]["data"]["attributesOffset"]
        patch.append((fullAttributesOffset + gravityOffset, b'\0\0\0\0'))

    return {data["sourceFile"]: patch}

parser = argparse.ArgumentParser(description="Generate patch data.")
parser.add_argument("datdumpsroot", help="The directory containing .dat json files.")
parser.add_argument("outfile", help="The json file to write the patch data to.")
parser.add_argument("--zerogravity", action="store_true", help="Adds data to the patch file that will set the gravity to 0 for all characters. This is useful so you can record aerial attacks without the hitbox interpolation distorting them by the character falling/rising.")
parser.add_argument("--disablegrabs", action="store_true", help="Changes all hitboxes with the grab effect to 'normal' so they will not all be rendered purple, but with the different colors they should have after being patched.")
args = parser.parse_args()

patch = {}
for file in os.listdir(args.datdumpsroot):
    path = os.path.join(args.datdumpsroot, file)
    if file.endswith(".json"):
        print(file)
        patch.update(getPatch(path, args.disablegrabs, args.zerogravity))

jsonPatch = {}
# preprocess before saving to json
for file in patch:
    jsonPatch[file] = []
    # save list of offset, byte-string (alternating)
    for i in range(len(patch[file])):
        jsonPatch[file].append(patch[file][i][0])
        jsonPatch[file].append(" ".join("{:02x}".format(byte) for byte in patch[file][i][1]))

# write out json file by hand to be a little bit more space efficient
with open(args.outfile, "w") as f:
    json.dump(jsonPatch, f)

# with open(args.outfile, "w") as f:
#     f.write("{\n")
#     for file in patch:
#         f.write('    "{}": [\n'.format(file))
#         for offset, data in patch[file]:
#             f.write('        [{}, "{}"],\n'.format(offset, data))
#         f.write("    ],\n")
#     f.write("}\n")
