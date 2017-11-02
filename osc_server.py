import re
import argparse
import math
from enum import Enum
from time import sleep
from pythonosc import dispatcher
from pythonosc import osc_server
from midi_interface import *

# 3rd layer isn't a clip layer in resolume
def layermap(idx):
    return colormap['green']
def padmap(layer_index):
    return colormap[['yellow', 'red', 'green', 'purple'][layer_index]]

# banks have selected and unselected only?
Bank = Enum('Bank', ['SEL', 'NOSEL'])
Pad = Enum('Pad', ['OFF', 'ON_1', "ON_2", "ON_3", "ON_4"])
PadState = [Pad.OFF] * 25
#LayerPadState = { n : PadState[:] for n in range(4) }
ClipState = [Pad.OFF] * 25
#BankState = [Bank.NOSEL] * 4
CurLayer = -1 #-> 3
CurBank = -1 #-> 3

def init_board():
    #board_on(colormap['white'])
    for b in banks:
        spot_on(b, colormap['red'])
    layer_select(1, True)

# Won't be called via handler, instead in response to midi sent from conspiracy
def bank_select(n):
    pass

def load_layer_pads():
    c_off = colormap['off']
    for i, state in enumerate(ClipState):
        if state == Pad.OFF:
            spot_on(pads[i], c_off)
            #pass
        else:
            layer_col = padmap(state.value - 2) 
            spot_on(pads[i], layer_col)
    print("loaded pads layer:{}---------------")

def layer_select(n, turn_on):
    global CurLayer
    if (n > 5 or n == 3): return
    if (n >= 3): n -= 1     # Account for routing layer
    n -= 1
    if turn_on is True:
        if n == CurLayer:
            print('\tignoring layer change')
            return
        c = layermap(n)
        spot_on(banks[n], c)
        CurLayer = n

        # Will require restoring later
        print("Swap color pads to CurLayer: {}".format(CurLayer))
        #pads_on(padmap(n))
        load_layer_pads()

    else:
        spot_on(banks[n], colormap['red'])
        print("layer select off: {}\n".format(n))


def layer_select_handler(addr, args):
    n = int(addr[6])
    print("layer select {}: {}".format(n, args))
    layer_select(n, args == 1)

def try_clip_select(layer, loc):
    owner = ClipState[loc]
    if owner == Pad.OFF:
        if layer >= 2: 
            l = layer + 2 
        else: 
            l = layer + 2
        newPad = Pad(l)
        ClipState[loc] = newPad
        print("ClipState[{}] => {}".format(loc, str(newPad)))
    else:
        print("--!!ClipState change block!!--")


def clip_select_handler(addr, args):
    # Update the Layer's Pad State, and the LEDs
    # If we change the layer then clip or vice versa quickly
    # is that going to reflect correctly using a global OSC?
    # May need to check that disconnects are coming from the 
    # current pad..
    # Is also going to wreck havok with autoplay....

    # Exception thrown: L2 playing clip from L1
    # layer change to L2 from L1
    # clip handler fires first
    # PadState updated on wrong layer

    #activelayer/clip/connect 1 not fired when switching layers
    # always seems to come right after clip_select when switching clips
    # delayed by transition time?

    # Clips must be owned by the first layer that plays them
    # Other layers attempting to play them are denied.
    y, x = [int(s) for s in re.findall(r'\d+', addr)]
    on = args == 1
    y = range(6)[-y]    # invert to translate to board
    loc = (y-1) * 5 + (x - 1)
    print("(y,x)({}{}) => {} --> {}".format(y, x, loc, args))

    if on:
        #sleep(0.2)        
        #c = colormap['white']
        #spot_on(pads[loc], c)
        #LayerPadState[CurLayer][loc] = Pad.ON
        try_clip_select(CurLayer, loc)
        #print("\tlayer:loc {}:{}  --> on".format(CurLayer, loc))
        load_layer_pads()
    else:
        #c = padmap(CurLayer)
        #spot_on(pads[loc], c)
        #LayerPadState[CurLayer][loc] = Pad.OFF
        #print("\tlayer:loc {}:{}  --> off".format(CurLayer, loc))
        ClipState[loc] = Pad.OFF
        print("ClipState[{}] => {}".format(loc, "Pad.OFF"))
        load_layer_pads()

def activelayer_clip_connect_handler(addr, args):
    print("\nactive layer clip connect args:{}".format(args))
    #if args == 1:
        #load_layer_pads()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
            default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
            type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()


    init_board()

    dispatcher = dispatcher.Dispatcher()
    #dispatcher.set_default_handler()
    #dispatcher.map("/debug", print)
    #dispatcher.map("/volume", print_volume_handler, "Volume")
    #dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)

    for i in range(8):
        dispatcher.map("/layer" + str(i) +  "/select", layer_select_handler)
    for x in range(1, 6):
        for y in range(1, 6):
            dispatcher.map("/layer{}/clip{}/connect".format(x, y), clip_select_handler)



    dispatcher.map("/activelayer/clip/connect", activelayer_clip_connect_handler)

    #server = osc_server.ThreadingOSCUDPServer(
    server = osc_server.BlockingOSCUDPServer(
              (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

    

  # /layerX/select
  # /layerX/clipX/connect
  # /layerX/clipX/preview

# Must setup default state of board, then handle recieving messages

def unhandled_print(unused_addr, args, volume):
    print("X: [{0}] ~ {1}".format(args[0], volume))

def print_volume_handler(unused_addr, args, volume):
    print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
    try:
        print("[{0}] ~ {1}".format(args[0], args[1](volume)))
    except ValueError: 
        pass

