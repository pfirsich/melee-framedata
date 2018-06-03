import os
import json
import argparse
import webbrowser as wb

def getFrameGraphData(summary):
    frameGraph = []
    lastHitFrame = None
    for frame in range(1, summary["totalFrames"] + 1):
        autoCancel = False
        if "landingLag" in summary:
            autoCancel = frame < summary["autoCancelBefore"]
            autoCancel = autoCancel or frame > summary["autoCancelAfter"]

        iasa = frame >= (summary["iasa"] or summary["totalFrames"] + 1)

        hitFrame = None
        for hf in summary["hitFrames"]:
            if frame >= hf["start"] and frame <= hf["end"]:
                hitFrame = hf

        h = 0
        if hitFrame:
            h = 1
            if lastHitFrame and lastHitFrame != hitFrame:
                h = 2
        a = int(autoCancel)
        i = int(iasa)
        frameGraph.append("a{}i{} h{}".format(a, i, h))

        lastHitFrame = hitFrame

    return frameGraph

def getFrameGraph(moveData):
    # Save Framegraph to HTML
    frameGraphData = getFrameGraphData(moveData)
    html = '<div class="framegraphwrapper">\n<table class="framegraph" cellspacing="0" cellpadding="0"><tbody>\n<tr>\n'
    legendHitbox, legendHitboxChanged, legendAutocancel, legendIasa = False, False, False, False
    for frameClass in frameGraphData:
        html += '\t<td class="{}"></td>\n'.format(frameClass)
        legendHitbox = legendHitbox or "h1" in frameClass
        legendHitboxChanged = legendHitboxChanged or "h2" in frameClass
        legendAutocancel = legendAutocancel or "a1" in frameClass
        legendIasa = legendIasa or "i1" in frameClass

    legend = []
    if legendAutocancel:
        legend.append('<span class="legend-autocancel">can auto-cancel</span>')
    if legendIasa:
        legend.append('<span class="legend-interrupt">can interrupt</span>')
    if legendHitbox:
        legend.append('<span class="legend-hitbox">&#x25CB;</span>: hitbox')
    if legendHitboxChanged:
        legend.append('<span class="legend-hitbox">&#x25CF;</span>: hitbox changed')

    html += """
</tr>
<tr>
    <td colspan="{}">
    <div class="legend">
        Legend: {}
    </div>
    </td>
</tr>
</tbody></table>
</div>

""".format(moveData["totalFrames"], ", ".join(legend))
    return html, all(frameClass == frameGraphData[0] for frameClass in frameGraphData)
