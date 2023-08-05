import pynes

if __name__ == "__main__":
    pynes.press_start()
    exit()

'''
from pynes.modules import nes_print \
    wait_vblank \
    load_sprite \
    rsset
'''


palette = []
asset = import_chr('player.png')

player_sprite = create_sprite('player', x, y, tile, palette_index)

def joypad1_up():
    sprite(0).y += 1

def joypad1_down():
    sprite(0).y -= 1

def joypad1_left():
    sprite(0).x -=1

def joypad1_right():
    sprite(0).y +=1

def reset():
    pynes.wait_vblank()
    load_palette(palette)
    load_sprite(player_sprite, 0)
