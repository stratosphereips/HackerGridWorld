#!/usr/bin/env python
# Server for the Hacker Grid World Reinforcement Learning
# Author: sebastian garcia, eldraco@gmail.com. First commit: Feb 5th 2023

import argparse
from datetime import datetime
import logging
import json

import asyncio

__version__ = 'v0.1'

async def server(host, port):
    """
    Start the socket server
    Define the function to deal with data
    """
    logger = logging.getLogger('SERVER')
    logger.info('Starting server')
    server = await asyncio.start_server(handle_new_client, host, port)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    logger.info(f'Serving on {addrs}')
    async with server:
        await server.serve_forever()

async def handle_new_client(reader, writer):
    """
    Function to deal with each new client
    """
    logger = logging.getLogger('SERVER')
    addr = writer.get_extra_info('peername')
    logger.info(f"Handling data from client {addr}")

    # Get a new world
    myworld = World()
    world = myworld.get_world()
    


    while True:
        answer = world
        # Convert world to json before sending
        world_json = json.dumps(world)
        logger.info(f"Sending: {world_json!r}")
        writer.write(bytes(str(world_json).encode()))
        await writer.drain()

        # Every x seconds, send it again
        #await asyncio.sleep(1)
        #writer.write(bytes(str(world_json).encode()))

        data = await reader.read(20)
        message = data.decode()

        myworld.input_key(message)

        logger.info(f"Received {message!r} from {addr}")


class World(object):
    """
    Class worl"
    """
    def __init__(self):
        """
        Initialize the web server
        Returns a dictionary
        """
        self.world_conf = confjson.get('world', None)
        self.size_x = self.world_conf.get('size_x', None)
        self.size_y = self.world_conf.get('size_y', None)
        self.character = {}
        self.character['icon'] = ":woman:"
        self.character['x'] = 5 
        self.character['y'] = 5 


        # Create the world as a list
        self.world = {}
        self.world["size"] = str(self.size_x) + 'x'+ str(self.size_y)
        self.world["score"] = 100

        self.positions = []
        # Fill with empty first
        #for pos in range(size_x*size_y):
            #positions.append("")

        """
        line0 = "XXXXXXXXXX"
        line1 = "X        X"
        line2 = "X        X"
        line3 = "X        X"
        line4 = "X        X"
        line5 = "X        X"
        line6 = "X        X"
        line7 = "X        X"
        line8 = "X        X"
        line9 = "XXXXXXXXXX"
        positions.extend(list(line0))
        positions.extend(list(line1))
        positions.extend(list(line2))
        positions.extend(list(line3))
        positions.extend(list(line4))
        positions.extend(list(line5))
        positions.extend(list(line6))
        positions.extend(list(line7))
        positions.extend(list(line8))
        positions.extend(list(line9))
        """

        # To do emoji by emoji
        # fill top and bottom
        """
        top_line = 0
        bottom_line = 9
        for x in range(size_x):
            positions[x + (top_line * size_x)] = ":bus:"
            positions[x + (bottom_line * size_x)] = ":bus:"

        # Fill vertical borders
        right_border = 9
        left_border = 0
        for y in range(size_y):
            positions[left_border + (y * 10)] = ":bus:"
            positions[right_border + (y * 10)] = ":bus:"
        """

        # Fill the middle rest with emojis
        #positions[21:28] = [":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[0:9] = [":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[10:19] = [":ram:",":locked:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[20:29] = [":ram:",":man:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[30:39] = [":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[40:49] = [":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[50:59] = [":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[60:69] = [":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[70:79] = [":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[80:89] = [":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]
        self.positions[90:99] = [":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:",":ram:"]

        # Invidivual emojis
        #y_line = 5
        #x_line = 5
        #self.positions[x_line + (y_line * self.size_x)] = ":ghost:"
        # Character
        self.positions[self.character['x'] + (self.character['y'] * self.size_x)] = self.character['icon']

        self.world["positions"] = self.positions

    def get_world(self):
        """
        Get the world
        """
        return self.world

    def input_key(self, key):
        """
        process keys
        """
        self.positions[self.character['x'] + (self.character['y'] * self.size_x)] = ":ram:"
        if "UP" in key:
            self.character['y'] -= 1
        elif "DOWN" in key:
            self.character['y'] += 1
        elif "RIGHT" in key:
            self.character['x'] += 1
        elif "LEFT" in key:
            self.character['x'] -= 1
        self.positions[self.character['x'] + (self.character['y'] * self.size_x)] = self.character['icon']




# Main
####################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Hacker Grid World Server version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Amount of verbosity. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Amount of debugging. This shows inner information about the flows.', action='store', required=False, type=int)
    parser.add_argument('-c', '--configfile', help='Configuration file.', action='store', required=True, type=str)

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s',)

    with open(args.configfile, 'r') as jfile:
        confjson = json.load(jfile)

    try:
        logging.debug('Server start')
        asyncio.run(server(confjson.get('HOST', None), confjson.get('PORT', None)))
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        logging.debug('Goodbye')