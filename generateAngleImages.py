size = 50
radius = size / 2 - 5
halfsize = size / 2
smallradius = 45 / 5

for i in range(361):
    with open("output/angleIcons/" + str(i) + ".svg", "w") as f:
        f.write("""
<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}">
    <circle cx="{hs}" cy="{hs}" r="{r}" stroke="grey" stroke-width="2" fill="none"/>
    <line x1="0" y1="0" x2="{r}" y2="0" stroke="red" stroke-width="3" transform="translate({hs}, {hs}) rotate({angle})"/>

   Sorry, your browser does not support inline SVG.
</svg>""".format(s=size, hs=halfsize, r=radius, angle=-i))

with open("output/angleIcons/361.svg", "w") as f:
    f.write("""
<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}">
    <circle cx="{hs}" cy="{hs}" r="{r}" stroke="grey" stroke-width="2" fill="none"/>
    <line x1="0" y1="0" x2="{r}" y2="0" stroke="red" stroke-width="2" transform="translate({hs}, {hs}) rotate(-44)"/>
    <line x1="0" y1="0" x2="{r}" y2="0" stroke="red" stroke-width="2" transform="translate({hs}, {hs}) rotate(-45)"/>
    <circle cx="{hs}" cy="{hs}" r="{sr}" fill="red"/>

   Sorry, your browser does not support inline SVG.
</svg>""".format(s=size, hs=halfsize, r=radius, sr=smallradius))
