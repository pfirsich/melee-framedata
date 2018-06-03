import os
import re
import sys
import json
import math

from ruamel.yaml import YAML
yaml = YAML()

from generalMoveNames import generalMoveNames
from generateFrameGraph import getFrameGraph

with open("moveNames.json") as f:
    moveNames = json.load(f)

#gfycatEmbed = "<div style='margin:0.5em 0 0.5em 0;position:relative;padding-bottom:54%'><iframe src='https://gfycat.com/ifr/{}' frameborder='0' scrolling='no' width='100%' height='100%' style='position:absolute;top:0;left:0' allowfullscreen></iframe></div>"
gfycatEmbed = "<div class='gfyitem' data-controls=true data-title=true data-responsive=true data-playback-speed=0.5 data-id={}></div>"

frameData = {}
frameDataPath = os.environ["FRAMEDATA"]
for file in os.listdir(frameDataPath):
    path = os.path.join(frameDataPath, file)
    if os.path.isfile(path):
        with open(path) as f:
            frameData[file.split(".")[0]] = json.load(f)

charConfigs = {}
sourcePath = "source"
for item in os.listdir(sourcePath):
    path = os.path.join(sourcePath, item)
    if os.path.isdir(path) and item != "Ice Climbers":
        with open(os.path.join(path, "config.yaml")) as f:
            charConfigs[item] = yaml.load(f)
            charConfigs[item]["name"] = item

def write(path, content):
    path = os.path.join("output", path)
    dirname = os.path.dirname(path)
    if len(dirname) > 0:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def template(sourceFile, **kwargs):
    if not os.path.isfile(sourceFile):
        #print("Template '{}' does not exist!".format(sourceFile))
        return ""
    with open(sourceFile) as f:
        html = f.read()
    for name, content in kwargs.items():
        html = html.replace("{{" + name + "}}", str(content))

    def templateIfMatch(match):
        var = match.group(1)
        if var in kwargs and kwargs[var]:
            return match.group(2)
        else:
            return ""
    html = re.sub(r"{{if (.*?)}}(.*?){{endif \1}}", templateIfMatch, html, flags=re.DOTALL)

    return html

def tag(tag, content, **kwargs):
    return "<{tag} {attrs}>{content}</{tag}>".format(
        tag=tag, content=content, attrs=" ".join('{}="{}"'.format(
            attr if not attr[0] == "_" else attr[1:], value) for attr, value in kwargs.items()))

def getCharLinks():
    chars = list((name, charConfigs[name]["pathName"]) for name in sorted(charConfigs))
    return "\n".join(tag("li", tag("a", name, _class="navlink",
        href="/{}/index.html".format(path))) for name, path in chars)

def generateIndexSite():
    navlinks = getCharLinks()
    index = template("source/index.html", navlinks=navlinks)
    nav = template("source/index.nav.html", navlinks=navlinks)
    base = template("base.html", title="Melee Framedata", nav=nav, contentbreadcrumbs="", content=index)
    write("index.html", base)

def frameRangeString(start, end):
    if start == end:
        return str(start)
    else:
        return "{}-{}".format(start, end)

def htmlAngle(angle):
    # This is not really entirely customizable from CSS (because of the image path)
    # I don't know how to fix this though
    title = angle
    if angle == 361:
        title = "Sakurai Angle"
    return '<span class="tip" title="{title}"><img class="angle" alt="{angle}" src="/angleIcons/{angle}.svg"></span>'.format(title=title, angle=angle)

# https://www.reddit.com/r/smashbros/comments/237zsv/formula_for_hitlag_in_melee/
def hitlag(damage, element, attacker, crouchCancel=False):
    if attacker:
        c = 1.0
        e = 1.0
    else: # character being hit
        c = 2/3 if crouchCancel else 1.0
        e = 1.5 if element == "electric" else 1.0
    return math.floor(c * math.floor(e * math.floor(3.0 + damage/3.0)))

def shieldstun(damage):
    return math.floor((damage + 4.45) / 2.235)

def getSummaryTable(moveData):
    columns = [("Total Frames", moveData["totalFrames"])]
    if moveData["iasa"] != None:
        columns.append(("IASA", moveData["iasa"]))
    if "landingLag" in moveData:
        columns.extend([
            ("Auto-Cancel Before", moveData["autoCancelBefore"]),
            ("Auto-Cancel After", moveData["autoCancelAfter"]),
            ("Landing Lag", moveData["landingLag"]),
            ("L-cancelled", moveData["lcancelledLandingLag"]),
        ])
    elif "throw" in moveData:
        columns.extend([
            ("Damage", moveData["throw"]["damage"]),
            ("Angle", htmlAngle(moveData["throw"]["angle"])),
            ("Knockback Scaling", moveData["throw"]["kbGrowth"]),
            ("Weight Dep. Knockback", moveData["throw"]["weightDepKb"]),
            ("Base Knockback", moveData["throw"]["baseKb"]),
            ("Element", moveData["throw"]["element"]),
        ])
        if "released" in moveData["throw"] and not moveData["throw"]["released"]:
            columns.append(("Cargo", "yes"))
    if "projectiles" in moveData:
        columns.append(("Projectile comes out", ", ".join(map(str, moveData["projectiles"]))))
    content = '<div class="summary">\n<h2>Summary</h2>\n<table>\n'
    for colName, colVal in columns:
        content += "\t<tr><th>{}</th><td>{}</td></tr>\n".format(colName, colVal)
    content += "</table>\n</div>\n\n"
    return content

hitboxGuidColors = [
    "red", "green", "yellow", "blue", "orange", "purple", "cyan", "magenta", "lime",
    "pink", "teal", "lavender", "brown", "beige", "maroon", "mint", "olive", "coral", "navy"
]

def getHitboxTables(moveData):
    hitboxGuidToNameHTML = lambda x: '<span class="hitbox_{0}">{0}</span>'.format(hitboxGuidColors[x])

    content = '<div class="hitboxes">\n<h2>Hitboxes</h2>\n'
    hitFrames = moveData["hitFrames"]
    sameHitboxesForAllHitframes = \
        all(hitFrame["hitboxes"] == hitFrames[0]["hitboxes"] for hitFrame in hitFrames)
    if sameHitboxesForAllHitframes:
        content += '<table class="hitframes_nocolors">\n<tr>'
        content += "<th>Hit Frames</th><td>{}</td>\n".format(
            ", ".join(frameRangeString(hitFrame["start"], hitFrame["end"]) for hitFrame in hitFrames))
        content += "</tr>"
    else:

        content += '<table class="hitframes_colors">\n'
        for hitFrame in hitFrames:
            translatedHitboxes = map(hitboxGuidToNameHTML, hitFrame["hitboxes"])
            content += "<tr><th>{}</th><td>{}</td></tr>\n".format(
                frameRangeString(hitFrame["start"], hitFrame["end"]),
                ", ".join(translatedHitboxes))
    content += "</table>\n\n"

    hitboxNames = len(moveData["hitboxes"]) > 1
    shieldDamage = any(hitbox["shieldDamage"] > 0 for hitbox in moveData["hitboxes"])
    element = any(hitbox["element"] != "normal" for hitbox in moveData["hitboxes"])
    wdkb = any(hitbox["weightDepKb"] > 0 for hitbox in moveData["hitboxes"])

    hitlagTip = False
    for hitbox in moveData["hitboxes"]:
        hitlagAtk = hitlag(hitbox["damage"], hitbox["element"], attacker=True)
        hitlagDef = hitlag(hitbox["damage"], hitbox["element"], attacker=False)
        if hitlagAtk != hitlagDef:
            hitlagTip = True
            break

    content += """
<table class="hitboxtable">
\t<tr class="headings">
\t{}
\t<th>Damage</th>
\t{}
\t<th>Angle</th>
\t<th><span class="tip" title="Base Knockback">BKB</span></th>
\t<th><span class="tip" title="Knockback Scaling/Growth">KBS</span></th>
\t{}
\t{}
\t<th><span class="tip" title="Clang">C</span></th>
\t<th><span class="tip" title="Rebound">R</span></th>
\t<th><span class="tip" title="Hits Grounded">G</span></th>
\t<th><span class="tip" title="Hits Airborne">A</span></th>
\t<th>{}</th>
\t<th>Shieldstun</th>
\t</tr>

""".format("<th>Hitbox</th>" if hitboxNames else "",
    "<th>Shield Damage</th>" if shieldDamage else "",
    '<th><span class="tip" title="Set Knockback">SKB</span></th>' if wdkb else "",
    "<th>Element</th>" if element else "",
    '<span class="tip" title="Attacker/Defender">Hitlag</span>' if hitlagTip else "Hitlag")

    for i, hitbox in enumerate(moveData["hitboxes"]):
        content += "\t<tr>\n"
        if hitboxNames:
            content += "\t<td>{}</td>\n".format(hitboxGuidToNameHTML(i))
        content += "\t<td>{}</td>\n".format(hitbox["damage"])
        if shieldDamage:
            content += "\t<td>{}</td>\n".format(hitbox["shieldDamage"])
        content += "\t<td>{}</td>\n".format(htmlAngle(hitbox["angle"]))
        content += "\t<td>{}</td>\n".format(hitbox["baseKb"])
        content += "\t<td>{}</td>\n".format(hitbox["kbGrowth"])
        if wdkb:
            content += "\t<td>{}</td>\n".format(hitbox["weightDepKb"])
        if element:
            content += "\t<td>{}</td>\n".format(hitbox["element"] if hitbox["element"] != "normal" else "")

        clang = hitbox["hitboxInteraction"] >= 2
        rebound = hitbox["hitboxInteraction"] == 3
        yes, no, yesHeavy, noHeavy = "&#x2713;", "&#x2714;", "&#x2717;", "&#x2718;"
        content += "\t<td>{}</td>\n".format(yes if clang else noHeavy)
        content += "\t<td>{}</td>\n".format(yes if rebound else noHeavy)
        content += "\t<td>{}</td>\n".format(yes if hitbox["hitGrounded"] else noHeavy)
        content += "\t<td>{}</td>\n".format(yes if hitbox["hitAirborne"] else noHeavy)

        hitlagAtk = hitlag(hitbox["damage"], hitbox["element"], attacker=True)
        hitlagDef = hitlag(hitbox["damage"], hitbox["element"], attacker=False)
        hitlagStr = str(hitlagAtk)
        if hitlagAtk != hitlagDef:
            hitlagStr += "/" + str(hitlagDef)
        content += "\t<td>{}</td>\n".format(hitlagStr)

        content += "\t<td>{}</td>\n".format(shieldstun(hitbox["damage"]))
        content += "\t</tr>\n\n"

    content += "</table>\n</div>\n\n"

    return content

def getMoveContent(charConfig, moveName, moveData):
    content = ""

    gfycatLink = charConfig["gfycatLinks"].get(moveName, None)
    if gfycatLink:
        content += gfycatEmbed.format(gfycatLink) + "\n\n"

    content += getSummaryTable(moveData)

    frameGraphHtml, allTheSame = getFrameGraph(moveData)
    if not allTheSame:
        content += frameGraphHtml

    if len(moveData["hitboxes"]) > 0:
        content += getHitboxTables(moveData)

    return content

def generateMovePage(charConfig, moveGroupName, moves):
    charMoveNames = moveNames[charConfig["externalName"]]

    moveNameBase = moveGroupName.split("_")[0]
    realMoveName = charMoveNames.get(moveNameBase, None)
    generalMoveName = generalMoveNames[moveGroupName]

    breadcrumbs = breadcrumbs=tag("a", charConfig["externalName"], _class="navlink",
        href="/{}/index.html".format(charConfig["pathName"]))
    nav = template("source/movenav.html", zair=False, breadcrumbs=breadcrumbs,
        nspecial=charMoveNames["nspecial"], sspecial=charMoveNames["sspecial"],
        dspecial=charMoveNames["dspecial"], uspecial=charMoveNames["uspecial"])

    content = '<h1 class="movename">{}{}</h1>\n\n'.format(generalMoveName,
        " - " + realMoveName if realMoveName else "")

    content += template("source/{}/{}.html".format(charConfig["pathName"], moveGroupName))

    for move in moves:
        moveData = frameData[charConfig["name"]].get(move)
        if moveData:
            content += "<div>"
            if len(moves) > 1:
                if move in charConfig["moveNames"]:
                    moveName = charConfig["moveNames"][move]
                else:
                    moveName = generalMoveNames[move]
                    if move in charMoveNames:
                        moveName += " - " + charMoveNames[move]
                content += '<h1 class="">{}</h1>\n\n'.format(moveName)
            content += getMoveContent(charConfig, move, moveData)
            content += "</div>"

    base = template("base.html",
        title="Melee Framedata - {} - {}".format(charConfig["externalName"], generalMoveName),
        nav=nav, contentbreadcrumbs='<h3 class="contentbreadcrumbs">' + breadcrumbs + '</h3>',
        content=content)
    write("{}/{}.html".format(charConfig["pathName"], moveGroupName), base)

moveGroups = [
    ("jab", ["jab1", "jab2", "jab3", "rapidjabs_start", "rapidjabs_loop", "rapidjabs_end"]),
    ("ftilt", ["ftilt_h", "ftilt_m", "ftilt_l"]),
    ("utilt", ["utilt"]),
    ("dtilt", ["dtilt"]),
    ("fsmash", ["fsmash_h", "fsmash_m", "fsmash_l"]),
    ("usmash", ["usmash"]),
    ("dsmash", ["dsmash"]),
    ("dashattack", ["dashattack"]),
    ("grab", ["grab"]),
    ("dashgrab", ["dashgrab"]),
    ("nair", ["nair"]),
    ("fair", ["fair"]),
    ("bair", ["bair"]),
    ("uair", ["uair"]),
    ("dair", ["dair"]),
    ("fthrow", ["fthrow"]),
    ("bthrow", ["bthrow"]),
    ("uthrow", ["uthrow"]),
    ("dthrow", ["dthrow"]),
]

def generateCharacter(character):
    charConfig = charConfigs[character]
    charMoveNames = moveNames[charConfig["externalName"]]
    breadcrumbs = breadcrumbs=tag("a", charConfig["externalName"], _class="navlink",
            href="/{}/index.html".format(charConfig["pathName"]))
    nav = template("source/movenav.html", zair=False, breadcrumbs=breadcrumbs,
        nspecial=charMoveNames["nspecial"], sspecial=charMoveNames["sspecial"],
        dspecial=charMoveNames["dspecial"], uspecial=charMoveNames["uspecial"])
    characterIndex = "source/{}/index.html".format(character)
    if os.path.isfile(characterIndex):
        content = template(characterIndex)
    else:
        content = template("source/defaultCharIndex.html")
    content += '<div class="showsmall">\n' + nav + "</div>\n"
    base = template("base.html", title="Melee Framedata - " + charConfig["externalName"],
        nav=nav, contentbreadcrumbs="", content=content)
    write(charConfig["pathName"] + "/index.html", base)

    charMoveGroups = list((group, charConfig["moveGroups"][group]) for group in charConfig["moveGroups"])
    for moveGroupName, moves in moveGroups + charMoveGroups:
        generateMovePage(charConfig, moveGroupName, moves)

def main():
    generateIndexSite()

    for character in sorted(charConfigs):
        print("#", character)
        generateCharacter(character)

if __name__ == "__main__":
    main()
