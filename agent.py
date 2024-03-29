#!/usr/bin/env python
# Agent to automatically play the Hacker Grid World Reinforcement Learning
# Author: sebastian garcia, eldraco@gmail.com. First commit: Feb 5th 2023

import argparse
import logging
import json
import curses
import socket
import emoji
import numpy as np
import random


__version__ = 'v0.4'

class q_learning(object):
    """
    Learning models should have this API

    act(world): To receive a Game() object

    """
    def __init__(self, theworld):
        self.actions = ['KEY_UP', 'KEY_DOWN', 'KEY_LEFT', 'KEY_RIGHT']
        self.last_action = -1
        self.learning_rate = confjson.get('learning_rate', 0.1)
        self.epsilon_start = confjson.get('epsilon_start', 1)
        self.epsilon_end = confjson.get('epsilon_end', 0)
        self.max_episodes_epsilon = confjson.get('epsilon_max_episodes', 3000)
        self.epsilon = self.epsilon_start
        self.gamma = confjson.get('gamma', 0.9)
        self.n_episodes_evaluate = confjson.get('n_episodes_evaluate', 1)
        self.eval_every_n_episodes = confjson.get('eval_every_n_episodes', 100)
        self.world = {}
        self.world['size_x'] = theworld.size_x
        self.world['size_y'] = theworld.size_y
        self.current_state = theworld.current_state
        self.prev_state = self.current_state
        self.score = 0
        self.best_score = float('-inf')
        self.last_episode_scores = []
        self.last_eval_episode_scores = []
        self.reward = theworld.current_reward
        self.logger = logging.getLogger('qlearn')
        self.episodes = 0
        self.eval_episodes = 0
        self.end = theworld.end
        # By default we are not only evaluating a policy
        self.eval_mode = False

        # Where to save the models
        self.behavioral_model_filename = 'behavioral-model'
        self.target_model_filename = 'target-model'
        self.eval_model_filename = 'evaluated-model'

        # Q-table levels
        # GF stands of Ground Floor. Is the main q_table used when the game starts and it is independent of the 'state' to start
        self.q_table = {}
        self.current_qtable_level = 'GF'

        # If repaly mode, load the model
        if args.replayfile:
            # Load
            self.q_table = np.load(args.replayfile, allow_pickle=True)
            self.q_table = self.q_table.item()
            # Force no random
            self.epsilon_start = 0
            self.epsilon_end = 0
            self.epsilon = 0
        else:
            self.initialize_q_table(self.current_qtable_level)


    def initialize_q_table(self, level):
        """
        Init the q table values for the specified qtable level
        """
        # The q_table is a dictionary indexed by the 'state' that was used to 'enter' the table, called here the 'level'.
        # On each position it has a two dimensional vector of X positions of 'states', and each 'state' has a vector of 4 actions
        # The X positions are in a continous list
        # Example
        #  self.q_table = {'GF': [ [0.1, 0.2, 0.3, 0.4] , ... , [0.1, 0.2, 0.3, 0.4] ], '90': [ [0.1, 0.2, 0.3, 0.4] , ... , [0.1, 0.2, 0.3, 0.4] ]}
        #self.q_table = np.zeros((self.world['size_x'] * self.world['size_y'], len(self.actions)))
        try:
            _ = self.q_table[level] 
        except KeyError:
            self.logger.info(f'Creating a new q_table level for level {level}')
            self.q_table[level] = np.zeros((self.world['size_x'] * self.world['size_y'], len(self.actions)))

    def update_world(self, theworld):
        """
        Update world
        """
        # Store prev state
        self.prev_state = self.current_state
        self.current_state = theworld.current_state
        self.reward = theworld.current_reward
        self.score += theworld.current_reward
        self.end = theworld.end

    def act(self, world):
        """
        Receive a world
        Return an action

        When the episode finishes, we automatically receive the new world, so
        new states are ready.
        """
        # First select an action from the exploratory policy
        action = self.choose_action()
        return action

    def choose_action(self):
        """
        Choose an action following a policy
        """
        try:
            #self.logger.info('Choose action.')
            if not args.replayfile and not self.eval_mode:
                die = random.random()
                # How epsilon decays
                decay_rate = np.max( [(self.max_episodes_epsilon - self.episodes) / self.max_episodes_epsilon, 0])
                self.epsilon = (self.epsilon_start - self.epsilon_end ) * decay_rate + self.epsilon_end
                if die <= self.epsilon:
                    # Random action e-greedy
                    self.logger.info('Choosing random action.')
                    action = random.randint(0, len(self.actions) - 1)
                else:
                    # Choose the action that maximizes the value of this state
                    values_actions = self.q_table[self.current_qtable_level][self.current_state]
                    max_value = np.max(values_actions)
                    # See if the max value appeared many times, and if yes break ties by choosing randomly between those indexes
                    temp_values_actions = np.array(values_actions)
                    indexes = np.where(temp_values_actions == max_value)[0]
                    action = random.choice(indexes)
                    self.logger.info(f'Choosing policy action. Action: {self.actions[action]}. Value: {max_value} from {values_actions}')
            else:
                # We are in eval mode or replaying a policy. Do not randomize the selection of actions. No egreedy
                values_actions = self.q_table[self.current_qtable_level][self.current_state]
                max_value = np.max(values_actions)
                action = np.argmax(values_actions)
                self.logger.info(f'Eval mode: Choosing policy action. Action: {self.actions[action]}. Value: {max_value} from {values_actions}')

            # Store last action
            self.last_action = action

            action_name = self.actions[action]
            return action_name
        except Exception as e:
            self.logger.error(f'Error in choose_action: {e}')

    def learn(self, world):
        """
        Update the target policy to learn from the
        last step
        """
        # Update world
        self.update_world(world)

        # If we are replaying or evaluating, don't learn
        if not args.replayfile and not self.eval_mode:
            try:
                # At this point, the transition was already done to the new state. 
                # But we still didn't update the value of the previous state
                # self.current_state is the state after the transition
                # self.prev_state is the state before the transition
                # self.reward is the reward of the transition

                # To get the value of Q(s', a')
                # Select the action that maximices the current policy
                self.logger.info(f'Learning in level {self.current_qtable_level}')
                values_actions = self.q_table[self.current_qtable_level][self.current_state]
                max_value = np.max(values_actions)
                # See if the max value appeared many times, and if yes break ties by choosing randomly between those indexes
                temp_values_actions = np.array(values_actions)
                indexes = np.where(temp_values_actions == max_value)[0]
                state_action_idx_max_value = random.choice(indexes)

                # Update Q(s, a)
                self.logger.info(f'Prev state: {self.prev_state}. Step Reward: {self.reward}. Next state: {self.current_state}. Next StateMaxValue: {self.q_table[self.current_qtable_level][self.current_state][state_action_idx_max_value]}. Idx: {state_action_idx_max_value}')
                self.logger.info(f'\tBefore update. Action Values: {self.q_table[self.current_qtable_level][self.prev_state]}.')
                self.q_table[self.current_qtable_level][self.prev_state][self.last_action] = self.q_table[self.current_qtable_level][self.prev_state][self.last_action] + (
                                                self.learning_rate * (
                                                    self.reward + 
                                                    (self.gamma * self.q_table[self.current_qtable_level][self.current_state][state_action_idx_max_value]) - 
                                                    self.q_table[self.current_qtable_level][self.prev_state][self.last_action] 
                                                    ) 
                                                )
                self.logger.info(f'\tAfter  update. Action Values: {self.q_table[self.current_qtable_level][self.prev_state]}.')
            except Exception as e:
                self.logger.error(f'Error in learn: {e}')

        # Update in which level the agent is playing in the qtable
        if self.reward > 0:
            # We got some positive reward, so crate/move to the next level
            # If the level exists already, creation is ignored
            self.logger.info(f'Reward is {self.reward} and >0 so change to level {self.current_state}')
            self.initialize_q_table(level=self.current_state)
            self.current_qtable_level = self.current_state


    def game_ended(self):
        """
        End of episode
        """
        if not args.replayfile and not self.eval_mode:
            # We are in training mode

            self.last_episode_scores.append(self.score)
            self.logger.info(f'Episode ended. Score: {self.score}')
            self.episodes += 1

            if self.episodes % self.eval_every_n_episodes == 0:
                avg_scores = np.average(self.last_episode_scores)
                self.logger.critical(f'Summary of episodes elapsed: {self.episodes}. Avg Scores in last {self.eval_every_n_episodes} episodes: {avg_scores:.4f}. Epsilon: {self.epsilon:.5f}. Saving.')
                # Save txt
                with open(self.target_model_filename + '.txt', 'w+') as fi:
                    fi.write(str(self.q_table))
                # Save npy
                np.save(self.target_model_filename, self.q_table)
                # Delete the previous scores so the avg is of the last X
                self.last_episode_scores = []

                # Eval the current policy as test, without random for X episodes
                self.eval_mode = True
                self.logger.error(f'Starting Evaluation.')
                # We are going to do the first eval episode
                self.eval_episodes += 1

        elif self.eval_mode:
            # We are in evaluation mode of the current policy
            self.last_eval_episode_scores.append(self.score)
            self.logger.error(f'Eval Episode score: {self.score}. Eval Episodes elapsed: {self.eval_episodes}')

            if self.eval_episodes == self.n_episodes_evaluate:
                # End the evaluation

                avg_scores = np.average(self.last_eval_episode_scores)
                self.logger.critical(f'Eval episodes elapsed: {self.eval_episodes}. Avg Scores in last {self.n_episodes_evaluate} episodes: {avg_scores:.4f}. Saving.')
                # Save txt
                with open(self.eval_model_filename + '.txt', 'w+') as fi:
                    fi.write(str(self.q_table))
                # Save npy
                np.save(self.eval_model_filename, self.q_table)

                # Finished the evalution after some episodes
                self.eval_mode = False
                self.eval_episodes = 0
                self.last_eval_episode_scores = []
                self.logger.error(f'Ending Evaluation.')
            else:
                self.eval_episodes += 1
        # Reset to first level
        self.current_qtable_level = 'GF'

        # Reset the score to 0
        self.score = 0


class Game(object):
    """
    Game object
    """
    def __init__(self):
        self.size_x = 0
        self.size_y = 0
        self.world_score = 0
        #self.reward = 0
        self.world_positions = {}
        self.end = False
        self.current_state = -1
        self.current_reward = 0

def start_agent(w, sock):
    """
    Start the socket server
    Define the function to deal with data
    """
    try:

        logger = logging.getLogger('agent ')
        logger.info('starting agent')

        myworld = Game()

        # Get data from server
        net_data = sock.recv(2048)
        logger.info(f'Received: {net_data.decode()!r}')

        # Process data, print world
        process_data(myworld, net_data, w)

        # Here we load the model we want
        agent_model = q_learning(myworld)

        while True:
            # Check end
            if check_end(myworld):
                # The game ended
                agent_model.game_ended()
                # If in test mode, stop here
                if args.replayfile:
                    return True
                # Get the new map to reset
                net_data = sock.recv(2048)
                logger.info(f'Received: {net_data.decode()!r}')
                # Process data, print world
                # The world is resseted by the server, here we just load it
                process_data(myworld, net_data, w)

            # Get key from agent, the action
            key = agent_model.act(myworld)

            # Print the action
            print_action(key, myworld, w)

            if "KEY_UP" in key:
                sock.send(b'UP')
            elif "KEY_DOWN" in key:
                sock.send(b'DOWN')
            elif "KEY_RIGHT" in key:
                sock.send(b'RIGHT')
            elif "KEY_LEFT" in key:
                sock.send(b'LEFT')
            elif "q" in key:
                break
            else:
                key = ''
                sock.send(b' ')
            logger.info(f'Sending: {key!r}')

            # Get data from server
            net_data = sock.recv(2048)
            logger.info(f'Received: {net_data.decode()!r}')

            # Process data, print world
            process_data(myworld, net_data, w)

            # With this new data, now learn
            agent_model.learn(myworld)

    except Exception as e:
        logging.error(f'Error in start_agent: {e}')


def check_end(myworld):
    """
    Check if we reached the end
    """
    if myworld.end:
        # Game end
        logger = logging.getLogger('agent')
        #logger.info(f'Game ended: Score: {myworld.world_score}')
        logger.info('Game ended.')
        myworld.world_score = 0
        return True

def process_data(myworld, data, w):
    """
    Process the data sent by the server
    """
    try:
        # convert to dict
        data = json.loads(data)
        myworld.size_x = int(data['size'].split('x')[0])
        myworld.size_y = int(data['size'].split('x')[1])
        myworld.current_reward = data['reward']
        myworld.world_score += myworld.current_reward
        myworld.world_positions = data['positions']
        myworld.current_state = data['current_character_position']
        myworld.end = data['end']
        # Print positions
        minimum_y = 10
        # In the console graph Y grows going down and X grows to the right
        for x in range(myworld.size_x):
            for y in range(myworld.size_y):
                w.addstr(y + minimum_y, x, emoji.emojize(str(myworld.world_positions[x + (y * 10)])))
        # Print score
        w.addstr(minimum_y + myworld.size_y + 1, 0, f"Reward: {str(myworld.current_reward):>5}")
        w.addstr(minimum_y + myworld.size_y + 2, 0, f"Score: {str(myworld.world_score):>5}")


    except Exception as e:
        logging.error(f'Error in process_data: {e}')

def print_action(action, myworld, w):
    """
    Print the action from the agent
    """
    minimum_y = 10
    w.addstr(myworld.size_y + minimum_y + 3, 0, f'{action:<15}')
    w.refresh()


def main(w):
    """
    This function is called curses_main to emphasise that it is
    the logical if not actual main function, called by curses.wrapper.

    Its purpose is to call several other functions to demonstrate
    some of the functionality of curses.

    w is the curses window
    """

    # Print the banner
    w.addstr("---------------------\n")
    w.addstr("| Hacker Grid World |\n")
    w.addstr("---------------------\n")
    w.refresh()

    # Get the socket of communication
    server = args.server
    port = args.port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server, port))

    # Start the agent
    start_agent(w, sock)

    sock.close()

# Main
####################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser = argparse.ArgumentParser(description=f"Client for humans of th Hacker Grid World Server. Version {__version__}. Author: Sebastian Garcia, eldraco@gmail.com", usage='%(prog)s -n <screen_name> [options]')
    parser.add_argument('-v', '--verbose', help='Amount of verbosity. This shows more info about the results.', action='store', required=False, type=int)
    parser.add_argument('-d', '--debug', help='Amount of debugging. This shows inner information about the flows. INFO, DEBUG, ERROR, CRITICAL', action='store', required=False, type=str)
    parser.add_argument('-s', '--server', help='IP of game server.', action='store', required=False, type=str, default='127.0.0.1')
    parser.add_argument('-p', '--port', help='Port of game server.', action='store', required=False, type=int, default=9000)
    parser.add_argument('-c', '--configfile', help='Configuration file.', action='store', required=True, type=str)
    parser.add_argument('-r', '--replayfile', help='Used this saved model strategy to play in human time.', action='store', required=False, type=str)

    args = parser.parse_args()
    logging.basicConfig(filename='agent.log', filemode='a', format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S',level=logging.CRITICAL)

    with open(args.configfile, 'r') as jfile:
        confjson = json.load(jfile)

    try:
        curses.wrapper(main)
    except Exception as e:
        logging.error(f'Error: {e}')
    finally:
        logging.debug('Goodbye')
