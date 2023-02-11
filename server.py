#!/usr/bin/env python
# Server for the Hacker Grid World Reinforcement Learning
# Author: sebastian garcia, eldraco@gmail.com. First commit: Feb 5th 2023

import argparse
from datetime import datetime
import logging
import json
import time
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


async def send_world(writer, world_json):
    """
    send worl
    """
    writer.write(bytes(str(world_json).encode()))

async def handle_new_client(reader, writer):
    """
    Function to deal with each new client
    """
    logger = logging.getLogger('SERVER')
    addr = writer.get_extra_info('peername')
    logger.info(f"Handling data from client {addr}")

    # Get a new world
    myworld = Game_HGW(score=100)
    world_env = myworld.get_world()

    while True:
        answer = world_env

        # Convert world to json before sending
        world_json = json.dumps(world_env)

        logger.info(f"Sending: {world_json!r}")
        await send_world(writer, world_json)
        await writer.drain()

        data = await reader.read(20)
        message = data.decode()

        myworld.input_key(message)

        logger.info(f"Received {message!r} from {addr}")


class Game_HGW(object):
    """
    Class Game_HGW
    Organizes and implements the logic of the game
    """
    def __init__(self, score=100):
        """
        Initialize the web server
        Returns a dictionary

        The game has a world, with characters and positions
        it also has rules, scores actions and dynamics of movements
        """
        self.conf = confjson.get('world', None)
        # Create the world as a dict
        self.world = {}
        self.world["size_x"] = self.conf.get("size_x", None)
        self.world["size_y"] = self.conf.get("size_y", None)
        self.world["min_x"] = 0
        self.world["min_y"] = 0
        # size_x and size_y are the length, but it starts in 0
        self.world["max_x"] = self.world["size_x"] - 1
        self.world["max_y"] = self.world["size_y"] - 1
        self.world["size"] = str(self.world["size_x"]) + 'x'+ str(self.world["size_y"])
        self.world["score"]= score
        self.world["positions"] = []

        # Set character
        self.character = {}
        self.character['icon'] = "W"
        self.character['x'] = 5 
        self.character['y'] = 5 

        # Goal of world
        self.goal = {}
        self.goal['icon'] = "X"
        self.goal['x'] = 9 
        self.goal['y'] = 0 
        self.goal['score'] = 100 
        self.goal['taken'] = False 
        self.move_penalty = 1

        # Set end
        self.world['end'] = False

        # Iconography
        self.background = ' '

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
        self.world['positions'][0:9] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]
        self.world['positions'][10:19] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]
        self.world['positions'][20:29] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]
        self.world['positions'][30:39] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]
        self.world['positions'][40:49] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]
        self.world['positions'][50:59] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]
        self.world['positions'][60:69] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]
        self.world['positions'][70:79] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]
        self.world['positions'][80:89] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]
        self.world['positions'][90:99] = [self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background,self.background]

        # Invidivual emojis
        #y_line = 5
        #x_line = 5
        #self.positions[x_line + (y_line * self.size_x)] = ":ghost:"

        # Goal
        self.world['positions'][self.goal['x'] + (self.goal['y'] * self.world['size_x'])] = self.goal['icon']

        # Character
        self.world['positions'][self.character['x'] + (self.character['y'] * self.world['size_x'])] = self.character['icon']

    def get_world(self):
        """
        Get the world
        """
        return self.world

    def check_boundaries(self):
        """
        Check boundaries of world and character 
        """
        # Check boundaries
        if self.character['x'] >= self.world['max_x']:
            self.character['x'] = self.world['max_x']
        elif self.character['x'] <= self.world['min_x']:
            self.character['x'] = self.world['min_x']

        if self.character['y'] >= self.world['max_y']:
            self.character['y'] = self.world['max_y']
        elif self.character['y'] <= self.world['min_y']:
            self.character['y'] = self.world['min_y']

    def check_goal(self):
        """
        Check goal of world and character 
        """
        # Check goal
        if self.character['x'] == self.goal['x'] and self.character['y'] == self.goal['y'] and not self.goal['taken']:
            self.world['score'] += self.goal['score']
            self.goal['taken'] = True

    def check_end(self):
        """
        Check the end
        """
        if self.world['score'] <= 0:
            self.world['end'] = True
        elif self.goal['taken'] == True:
            self.world['end'] = True

    def input_key(self, key):
        """
        process keys
        """
        self.check_end()

        # Move character
        self.world['positions'][self.character['x'] + (self.character['y'] * self.world['size_x'])] = self.background
        if "UP" in key:
            self.character['y'] -= 1
        elif "DOWN" in key:
            self.character['y'] += 1
        elif "RIGHT" in key:
            self.character['x'] += 1
        elif "LEFT" in key:
            self.character['x'] -= 1

        self.check_boundaries()

        self.check_goal()

        # Move character
        logging.info(self.character)
        self.world['positions'][self.character['x'] + (self.character['y'] * self.world['size_x'])] = self.character['icon']
        self.world['score'] -= self.move_penalty

        # Cooldown period
        # Each key inputted is forced to wait a little
        time.sleep(0.1)




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