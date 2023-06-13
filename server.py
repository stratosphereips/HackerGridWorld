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
        try:
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
        except Exception as e:
            logger.info(f"Client disconnected: {e}")
            break


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
        it also has rules, rewards actions and dynamics of movements
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
        self.world["reward"] = confjson['world'].get("reward", 0)
        # Positions are stored as continous list, from 0 to 99 (for 100 positions example)
        self.world["positions"] = []
        # Track the end
        self.world['end'] = False
        # Move penalty
        self.move_penalty = -1
        # Max steps
        self.steps = confjson['max_steps']

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
            # The objects are loaded as pos = X + (Y * X_size)
            self.world['positions'][
                    self.objects[object]['x']
                    + (self.objects[object]['y']
                        * self.world['size_x'])
                    ] = self.objects[object]['icon']

        logging.info(f"Objects: {self.objects}")

        # Add the fixed objects
        # self.put_fixed_items()

    def put_fixed_items(self):
        """
        Add the fixed items
        """
        # output gate
        for object in self.objects:
            # positions
            if not 'character' in object:
                if self.objects[object]['consumable'] == False or (self.objects[object]['consumable'] == True and self.objects[object]['taken'] == False):
                    # The objects are loaded as pos = X + (Y * X_size)
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
                        self.world['reward'] = self.objects[object]['reward']
                        self.objects[object]['taken'] = True


    def check_end(self):
        """
        Check the end

        Two OR conditions
        - If steps is 0 then the game ends
        - If the output gate was crossed, the game ends
        """
        logging.info('Checking end')
        if self.steps <= 0:
            self.world['end'] = True
            logging.info('World end by timoutout')
            return True
        for obj in self.objects:
            try:
                if self.objects[obj]['ends_game'] == True:
                    if self.objects[obj]['taken'] == True:
                        logging.info(f'World end by gate: {obj}')
                        self.world['end'] = True
                        return True
            except KeyError:
                # Some objects dont have the key 'ends_game'
                pass
        return False

    def check_walls(self, x, y):
        """
        Check if the object in the position character+x, character+y is solid or not
        """
        proposed_x = self.objects['character']['x'] + x
        proposed_y = self.objects['character']['y'] + y
        for object in self.objects:
            if not 'character' in object:
                if self.objects[object]['x'] == proposed_x and self.objects[object]['y'] == proposed_y and self.objects[object]['solid'] == True:
                    return True
        return False

    def process_input_key(self, key):
        """
        process input key
        """
        # The world positions is a 100-values vector (in 100 states)
        # X (horizontal in the grid) goes from 0 to 9 to the right, Y (vertical in the grid) goes from 0 to 9 down
        # The top-left corner is X=0, Y=0
        # The lower-right corner is X=9, Y=9
        # The position vector starts with all the X positions for Y=0, then all the X positions for Y=1, etc.
        # [Y0X0, Y0X1, ..., Y0X9, Y1X0, Y1X1, ..., Y9X9]

        # To transform from a X, Y system to the large position vector that goes from 0 to 99 we do
        # position = X + (Y * 10)
        # examples
        #  X=0, Y=0 -> pos=0
        #  X=9, Y=0 -> pos=9
        #  X=8, Y=0 -> pos=8
        #  X=3, Y=1 -> pos=13
        #  X=0, Y=9 -> pos=90

        # Find the new positions of the character
        # Delete the current character
        self.world['positions'][self.objects['character']['x'] + (self.objects['character']['y'] * self.world['size_x'])] = self.background
        if "UP" in key:
            # Check that the boundaries of the game were not violated
            if not self.check_walls(0, -1):
                self.objects['character']['y'] -= 1
        elif "DOWN" in key:
            if not self.check_walls(0, 1):
                self.objects['character']['y'] += 1
        elif "RIGHT" in key:
            if not self.check_walls(1, 0):
                self.objects['character']['x'] += 1
        elif "LEFT" in key:
            if not self.check_walls(-1, 0):
                self.objects['character']['x'] -= 1
        logging.info(f"The char was moved to {self.objects['character']['x']} {self.objects['character']['y']} ")

        # Compute the character move penalty in reward
        self.world['reward'] = self.move_penalty
        # Decrease one step
        self.steps -= 1

        # Check that the boundaries of the game were not violated
        self.check_boundaries()

        # Check if there were any collisions
        self.check_collisions()

        # Check if the game ended
        self.check_end()

        # Move the character
        self.world['positions'][self.objects['character']['x'] + (self.objects['character']['y'] * self.world['size_x'])] = self.objects['character']['icon']
        self.world['current_character_position'] = self.objects['character']['x'] + (self.objects['character']['y'] * self.world['size_x'])

        # Put fixed objects back
        self.put_fixed_items()

        logging.info(f"Score after key: {self.world['reward']}")

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
    parser.add_argument('-t', '--test', help='Run serve in test mode. Speed is 0.1 and port is the port in the conf + 1', action='store_true', required=False)

    args = parser.parse_args()
    logging.basicConfig(filename='server.log', filemode='a', format='%(asctime)s, %(name)s: %(message)s', datefmt='%H:%M:%S', level=logging.CRITICAL)

    with open(args.configfile, 'r') as jfile:
        confjson = json.load(jfile)
        if args.test:
            confjson['speed'] = 0.1
            confjson['port'] = confjson['port'] + 1

    try:
        logging.debug('Server start')
        asyncio.run(server(confjson.get('host', None), confjson.get('port', None)))
    except KeyboardInterrupt:
        logging.debug('Terminating by KeyboardInterrupt')
        raise SystemExit
    except Exception as e:
        logging.error(f'Exception in __main__: {e}')
    finally:
        logging.debug('Goodbye')
