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
    Send the world to the client
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
    myworld = Game_HGW()
    world_env = myworld.get_world()

    # Send the first world
    # Convert world to json before sending
    world_json = json.dumps(world_env)
    logger.info(f"Sending: {world_json!r}")
    await send_world(writer, world_json)
    await writer.drain()

    while True:

        data = await reader.read(20)
        message = data.decode()

        logger.info(f"Received {message!r} from {addr}")

        myworld.process_input_key(message)

        # Convert world to json before sending
        world_json = json.dumps(world_env)

        logger.info(f"Sending: {world_json!r}")
        await send_world(writer, world_json)
        try:
            await writer.drain()
        except ConnectionResetError:
            logger.info(f'Connection lost. Client disconnected.')

        # If the game ended, reset and resend
        if myworld.world['end']:
            del myworld

            myworld = Game_HGW()
            world_env = myworld.get_world()

            # Necessary to give time to the socket to send the old world before sending the new. If not they look like one message
            time.sleep(0.01)

            # Send the first world
            # Convert world to json before sending
            world_json = json.dumps(world_env)
            logger.info(f"Sending: {world_json!r}")
            await send_world(writer, world_json)
            try:
                await writer.drain()
            except ConnectionResetError:
                logger.info(f'Connection lost. Client disconnected.')



class Game_HGW(object):
    """
    Class Game_HGW
    Organizes and implements the logic of the game
    """
    def __init__(self):
        """
        Initialize the game env
        Returns a game object

        The game has a world, with characters and positions
        it also has rules, scores actions and dynamics of movements
        """
        # Read the conf
        with open(args.configfile, 'r') as jfile:
            confjson = json.load(jfile)

        # Create the world as a dict
        logging.info(f"Starting a new world")
        self.world = {}
        self.world["size_x"] = confjson['world'].get("size_x", None)
        self.world["size_y"] = confjson['world'].get("size_y", None)
        self.world["min_x"] = 0
        self.world["min_y"] = 0
        # size_x and size_y are the length
        self.world["max_x"] = self.world["size_x"] - 1
        self.world["max_y"] = self.world["size_y"] - 1
        self.world["size"] = str(self.world["size_x"]) + 'x'+ str(self.world["size_y"])
        self.world["score"] = confjson['world'].get("score", 500)
        self.prev_score = self.world["score"]
        # Positions are stored as continous list, from 0 to 99 (for 100 positions example)
        self.world["positions"] = []
        # Move penalty
        self.move_penalty = 1
        # Track the end
        self.world['end'] = False


        # Iconography
        self.background = ' '

        # Fill the positions of the world with background
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

        # Load all objects in the world
        self.objects = confjson['objects']
        logging.info(f"conf obj: {confjson['objects']}")

        # The character object is special, needs to be in the world for the client
        self.world['current_character_position'] = self.objects['character']['x'] + (self.objects['character']['y'] * self.world['size_x'])

        # Init objects that do need to appear in the world for the client
        for object in self.objects:
            # positions
            self.world['positions'][
                    self.objects[object]['x']
                    + (self.objects[object]['y']
                        * self.world['size_x'])
                    ] = self.objects[object]['icon']

        logging.info(f"Objects: {self.objects}")

        """
        self.character = {}
        self.character['icon'] = "W"
        self.character['x'] = confjson['objects']['character']["start_position_x"]
        self.character['y'] = confjson['objects']['character']["start_position_y"]
        # Set the state of the character in the world
        self.world['current_character_position'] = self.character['x'] + (self.character['y'] * self.world['size_x'])

        # Goal of world
        self.goal = {}
        self.goal['icon'] = "X"
        self.goal['x'] = 9
        self.goal['y'] = 0
        self.goal['score'] = 500
        self.goal['taken'] = False

        # Output gate of world
        self.output_gate = {}
        self.output_gate['icon'] = "O"
        self.output_gate['x'] = 9
        self.output_gate['y'] = 9
        self.output_gate['score'] = 500
        self.output_gate['taken'] = False
        """



        """
        # Goal
        self.world['positions'][self.goal['x'] + (self.goal['y'] * self.world['size_x'])] = self.goal['icon']

        # Character
        self.world['positions'][self.character['x'] + (self.character['y'] * self.world['size_x'])] = self.character['icon']
        """

        # Add the fixed objects
        # self.put_fixed_items()

    def put_fixed_items(self):
        """
        Add the fixed items
        """
        # output gate
        #self.world['positions'][self.objects['output_gate']['x'] + (self.objects['output_gate']['y'] * self.world['size_x'])] = self.objects['output_gate']['icon']
        for object in self.objects:
            # positions
            if not 'character' in object:
                if self.objects[object]['consumable'] == False or (self.objects[object]['consumable'] == True and self.objects[object]['taken'] == False):
                    self.world['positions'][
                            self.objects[object]['x']
                            + (self.objects[object]['y']
                                * self.world['size_x'])
                            ] = self.objects[object]['icon']

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
        if self.objects['character']['x'] >= self.world['max_x']:
            self.objects['character']['x'] = self.world['max_x']
        elif self.objects['character']['x'] <= self.world['min_x']:
            self.objects['character']['x'] = self.world['min_x']

        if self.objects['character']['y'] >= self.world['max_y']:
            self.objects['character']['y'] = self.world['max_y']
        elif self.objects['character']['y'] <= self.world['min_y']:
            self.objects['character']['y'] = self.world['min_y']

    def check_collisions(self):
        """
        Check goal of world and other collisions
        """
        for object in self.objects:
            # positions
            if not 'character' in object:
                if self.objects[object]['consumable'] == False or (self.objects[object]['consumable'] == True and self.objects[object]['taken'] == False):
                    if self.objects[object]['x'] == self.objects['character']['x'] and self.objects[object]['y'] == self.objects['character']['y']:
                        self.world['score'] += self.objects[object]['score']
                        self.objects[object]['taken'] = True


        """
        # Check objects
        if self.objects['character']['x'] == self.objects['goal']['x'] and self.objects['character']['y'] == self.objects['goal']['y'] and not self.objects['goal']['taken']:
            if not self.objects['goal']['taken']:
                self.world['score'] += self.objects['goal']['score']
                self.objects['goal']['taken'] = True

        # Check output_gate
        if self.objects['character']['x'] == self.objects['output_gate']['x'] and self.objects['character']['y'] == self.objects['output_gate']['y'] and not self.objects['output_gate']['taken']:
            if not self.objects['output_gate']['taken']:
                self.world['score'] += self.objects['output_gate']['score']
                self.objects['output_gate']['taken'] = True
        """

    def check_end(self):
        """
        Check the end

        Two OR conditions
        - If the score is 0 then the game ends
        - If the output gate was crossed, the game ends
        """
        if self.world['score'] <= 0:
            self.world['end'] = True
            return True
        if self.objects['output_gate']['taken'] == True:
            self.world['end'] = True
            return True
        return False

    def process_input_key(self, key):
        """
        process input key
        """

        # Find the new positions of the character
        # Delete the current character
        self.world['positions'][self.objects['character']['x'] + (self.objects['character']['y'] * self.world['size_x'])] = self.background
        if "UP" in key:
            self.objects['character']['y'] -= 1
        elif "DOWN" in key:
            self.objects['character']['y'] += 1
        elif "RIGHT" in key:
            self.objects['character']['x'] += 1
        elif "LEFT" in key:
            self.objects['character']['x'] -= 1
        logging.info(f"The char was moved to {self.objects['character']['x']} {self.objects['character']['y']} ")

        # Compute the character move penalty
        self.world['score'] -= self.move_penalty

        # Check that the boundaries of the game were not violated
        self.check_boundaries()

        # Check if there were any collitions
        self.check_collisions()

        # Check if the game ended
        self.check_end()

        # Move the character
        self.world['positions'][self.objects['character']['x'] + (self.objects['character']['y'] * self.world['size_x'])] = self.objects['character']['icon']
        self.world['current_character_position'] = self.objects['character']['x'] + (self.objects['character']['y'] * self.world['size_x'])

        # Put fixed objects back
        self.put_fixed_items()

        self.prev_score = self.world['score']

        logging.info(f"Score after key: {self.world['score']}")

        # Cooldown period
        # Each key inputted is forced to wait a little
        # This should be at least 0.1 for human play or replay mode
        # Should be 0 for agents to play
        time.sleep(confjson.get('speed', 0))


# Main
####################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Hacker Grid World Server version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Verbosity level. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Debugging level. This shows inner information about the flows.', action='store', required=False, type=int)
    parser.add_argument('-c', '--configfile', help='Configuration file.', action='store', required=True, type=str)

    args = parser.parse_args()
    logging.basicConfig(level=logging.ERROR, format='%(name)s: %(message)s',)

    with open(args.configfile, 'r') as jfile:
        confjson = json.load(jfile)

    try:
        logging.debug('Server start')
        asyncio.run(server(confjson.get('host', None), confjson.get('port', None)))
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        logging.debug('Goodbye')
