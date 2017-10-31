import re
import argparse
import math

from pythonosc import dispatcher
from pythonosc import osc_server

import midi_interface

# 3rd layer isn't a clip layer in resolume
layermap = ['red', 'blue', 'green', 'green', 'yellow']

# banks have selected and unselected only?
Bank = Enum('SELECTED', 'UNSELECTED')
Pad = Enum('OFF', 'ON_1','ON_2', 'ON_3', 'ON_4')
PadState = 



def unhandled_print(unused_addr, args, volume):
    print("X: [{0}] ~ {1}".format(args[0], volume))

def print_volume_handler(unused_addr, args, volume):
    print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
    try:
        print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

def layer_select(addr, args, volume):
    n = addr[6]
    if volume is 1:
        spot_on(banks[n], 'red')
    else:
        spot_on(banks[n], 'off')

def clip_connect(addr, args, volume):
    n, c = [int(s) for s in re.findall(r'\d+', addr)]
    if volume is 1:
        spot_on(pads[c], layermap[n])
    else:
        spot_on(pads[c], 'white')



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
            default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
            type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.set_default_handler(unhandled_print)
    dispatcher.map("/debug", print)
    dispatcher.map("/volume", print_volume_handler, "Volume")
    dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)

    dispatcher.map("/layer?/select", layer_select)
    dispatcher.map("/activelayer/clip/connect", print)

    server = osc_server.ThreadingOSCUDPServer(
              (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()

    board_on('white')

  # /layerX/select
  # /layerX/clipX/connect
  # /layerX/clipX/preview

# Must setup default state of board, then handle recieving messages

