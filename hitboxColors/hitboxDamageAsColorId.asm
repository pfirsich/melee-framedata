# heavily based on:
# https://smashboards.com/threads/custom-hitbox-id-colors.427023/
# https://smashboards.com/threads/hitbox-color-darkens-based-on-damage.454256/
# colors:
# at beginning of CollisionBubbles_HitboxDisplay

lwz r0, 0(r3) # default code line, load hitbox active bool

lwz r5, 0x8(r3) # get hitbox damage


cmpwi r5, 0
beq RED

cmpwi r5, 1
beq GREEN

cmpwi r5, 2
beq YELLOW

cmpwi r5, 3
beq BLUE

cmpwi r5, 4
beq ORANGE

cmpwi r5, 5
beq PURPLE

cmpwi r5, 6
beq CYAN

cmpwi r5, 7
beq MAGENTA

cmpwi r5, 8
beq LIME

cmpwi r5, 9
beq PINK

cmpwi r5, 10
beq TEAL

cmpwi r5, 11
beq LAVENDER

cmpwi r5, 12
beq BROWN

cmpwi r5, 13
beq BEIGE

cmpwi r5, 14
beq MAROON

cmpwi r5, 15
beq MINT

cmpwi r5, 16
beq OLIVE

cmpwi r5, 17
beq CORAL

# link actually has 17 distinct hitboxes
# on his aerial up b. wtf.
cmpwi r5, 18
beq NAVY


# default color
b GREY


RED:
lis r5, 0xe619
ori r5, r5, 0x4ba0
b COLOR_FINISH

GREEN:
lis r5, 0x3cb4
ori r5, r5, 0x4ba0
b COLOR_FINISH

YELLOW:
lis r5, 0xffe1
ori r5, r5, 0x19a0
b COLOR_FINISH

BLUE:
lis r5, 0x0082
ori r5, r5, 0xc8a0
b COLOR_FINISH

ORANGE:
lis r5, 0xf582
ori r5, r5, 0x31a0
b COLOR_FINISH

PURPLE:
lis r5, 0x911e
ori r5, r5, 0xb4a0
b COLOR_FINISH

CYAN:
lis r5, 0x46f0
ori r5, r5, 0xf0a0
b COLOR_FINISH

MAGENTA:
lis r5, 0xf032
ori r5, r5, 0xe6a0
b COLOR_FINISH

LIME:
lis r5, 0xd2f5
ori r5, r5, 0x3ca0
b COLOR_FINISH

PINK:
lis r5, 0xfabe
ori r5, r5, 0xbea0
b COLOR_FINISH

TEAL:
lis r5, 0x0080
ori r5, r5, 0x80a0
b COLOR_FINISH

LAVENDER:
lis r5, 0xe6be
ori r5, r5, 0xffa0
b COLOR_FINISH

BROWN:
lis r5, 0xaa6e
ori r5, r5, 0x28a0
b COLOR_FINISH

BEIGE:
lis r5, 0xfffa
ori r5, r5, 0xc8a0
b COLOR_FINISH

MAROON:
lis r5, 0x8000
ori r5, r5, 0x00a0
b COLOR_FINISH

MINT:
lis r5, 0xaaff
ori r5, r5, 0xc3a0
b COLOR_FINISH

OLIVE:
lis r5, 0x8080
ori r5, r5, 0x00a0
b COLOR_FINISH

CORAL:
lis r5, 0xffd8
ori r5, r5, 0xb1a0
b COLOR_FINISH

NAVY:
lis r5, 0x0000
ori r5, r5, 0x80a0
b COLOR_FINISH



GREY:
lis r5, 0x8080
ori r5, r5, 0x80a0

COLOR_FINISH:
stw r5,-0x8000(r13) # store color @804d36a0 = hitbox RGBA value

