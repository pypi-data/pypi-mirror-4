# -*- coding: utf-8 -*-

from pynes.c6502 import opcodes

class Asm(object):

    def __init__(self):
        object.__setattr__(self,'bin', [])

    def __getattr__(self,name):
        if name.upper() in opcodes:
            opcode = opcodes[name.upper()]
            if 'sngl' in opcode:
                object.__getattribute__(self, 'bin').append(opcode['sngl'])
                return opcode['sngl']
            raise Exception('instruction %s dosent support implied address mode' & name)
        raise AttributeError("%r object has no attribute %r" % (type(self).__name__, name))

    def __setattr__(self, name, value):
        if name.upper() in opcodes:
            opcode = opcodes[name.upper()]
            arg2 = False
            if isinstance(value, str):
                address_mode = 'imm'
                value = int(value)
                if value > 0xff:
                    arg1 = (value & 0x00ff)
                    arg2 = (value & 0xff00) >> 8
                else:
                    arg1 = value
            elif isinstance(value, int):
                address_mode = 'abs'
                if value > 0xff:
                    arg1 = (value & 0x00ff)
                    arg2 = (value & 0xff00) >> 8
                else:
                    arg1 = value
            if address_mode in opcode:
                object.__getattribute__(self, 'bin').extend([opcode[address_mode], arg1])
                if arg2:
                    object.__getattribute__(self, 'bin').append(arg2)
                return opcode[address_mode]

            raise Exception('instruction %s dosent support implied address mode' & name)
        raise AttributeError("%r object has no attribute %r" % (type(self).__name__, name))

    def debug(self):
        for c in object.__getattribute__(self, 'bin'):
            print hex(c)

    def f_byt(self):
        pass


class cc65(Asm):
    pass


class Game:

    def prg(self):
        pass

    def reset(self):
        pass

    def title_screen(self):
        pass

    def loop(self):
        pass

    def options(self):
        pass

    def compile(self):
        pass
