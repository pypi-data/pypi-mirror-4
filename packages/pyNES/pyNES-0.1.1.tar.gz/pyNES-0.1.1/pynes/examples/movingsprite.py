import pynes

from pynes.bitbag import *  

if __name__ == "__main__":
    pynes.press_start()
    exit()

palette = [ 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
        0x0F, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 59,
        60, 61, 62, 63 ]

asset = import_chr('player.png')

player_sprite = create_sprite(asset, 0x80, 0x80, [0])

def joypad1_up():
    sprite(0).y += 1

def joypad1_down():
    sprite(0).y -= 1

def joypad1_left():
    sprite(0).x -=1

def joypad1_right():
    sprite(0).y +=1

def reset():
    global palette, player_sprite
    pynes.wait_vblank()
    load_palette(palette)
    load_sprite(player_sprite, 0)
    infinity_loop()