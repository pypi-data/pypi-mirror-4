from pynes.sdk import Game, cc65, Asm

PPUCTRL = 0x2000
PPUMASK = 0x2001
PPUSTATUS = 0x2002

class Roulette(Game):

    def zeropage(self):
        asm = Asm()
        self.nmis = asm.f_res(1)

    def ineshdr(self):
        asm = Asm()
        asm.f_byt('NES', 0x1a)
        asm.f_byt(1) #16 KiB PRG ROM
        asm.f_byt(1) #8 KiB CHR ROM
        asm.f_byt(1) #vertical mirroring; low mapper nibble: 0
        asm.f_byt(0) #high mapper nibble: 0

    def vectors(self):
        pass

    def irq(self):
        asm = Asm()
        asm.rti
        return asm

    def nmi(self):
        asm = Asm()
        #asm.inc nmis
        asm.rti

    def reset(self):
        asm = Asm()
        asm.sei
        asm.ldx = '0'
        asm.stx = PPUCTRL   # disable vblank NMI
        asm.stx = PPUMASK   # disable rendering (and rendering-triggered mapper IRQ)
        asm.lda = str(0x40)
        asm.sta = 0x4017    # disable frame IRQ
        asm.stx = 0x4010    # disable DPCM IRQ
        asm.bit = PPUSTATUS # ack vblank NMI
        asm.bit = 0x4015    # ack DPCM IRQ
        asm.cld             # disable decimal mode to help generic 6502 debuggers
        asm.dex             # set up the stack
        asm.txs
        return asm.bin

    def get_code(self):
        code = []
        code.extend(self.reset())
        return code
