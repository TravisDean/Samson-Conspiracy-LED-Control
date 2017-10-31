import mido
from time import sleep
from random import choice, randrange

try: 
    out = mido.open_output('Conspiracy 4')
except RuntimeError:
    print(str(e))
    outs = mido.get_output_names()
    for o in outs:
        print(o)



colormap = {'off': '1C', 'red': '15', 'yellow': '13', 'green': '16', 'blue': '18', 'purple': '19', 'light blue': '1A', 'white': '1B' }
colors = list(colormap.values())
board = range(0x0, 0x2F)
board = [format(b, '02X') for b in board]


#bank1x = ["90 0" + str(x) + " 2D" for x in range(0, 10)]

def spot_on(loc, hexcolor):
    m = mido.Message.from_hex("90 "+ loc +  " " + hexcolor)
    out.send(m)

def pad_on(hexcolor):
    [spot_on(loc, hexcolor) for loc in board[:25]]

def board_on(hexcolor):
    #hexcolor = format(hexint, 'X')
    bank1x = ["90 0" + format(x, 'X') + " " + hexcolor for x in range(0x0, 0x10)]
    bank1x += ["90 " + format(x, 'X') + " " + hexcolor for x in range(0x10, 0x2F)]
    #for b in bank1x:
        #print(b)

    bank1 = [mido.Message.from_hex(x) for x in bank1x]

    for b in bank1:
        out.send(b)
    print(str(bank1[0]))

def iterate_col():
    for c in range(0, 128):
        if (c < 0x10):
            col = "0" + format(c, 'X')
        else:
            col = format(c, 'X')
        input('col was ' + str(col) + " == " + format(c, 'b'))
        board_on(col)

def party():
    c = choice(colors)
    board_on(c)
    while True:
        l = choice(board)
        c = choice(colors)
        spot_on(l, c)
        sleep(0.02)


try:
    pad_on(colormap['yellow'])
    #party() 
    while True:
        h = input('hex to send: ')
        out.send(mido.Message.from_hex(str(h)))

    col = input('color? ')
    board_on(colormap[col])
except ValueError:
    print("Value Error.")
    out.close()
    print("Closed port")
