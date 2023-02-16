# Hacker Grid World
A client-server game to train and play with remote reinforcement learning in a Hacker Grid World.

<p align="center">
<img src="https://github.com/stratosphereips/HackerGridWorld/raw/main/agent.gif" width="450px" title="HGW in action.">
</p>



# How to Use

## Start the server

    git clone https://github.com/stratosphereips/HackerGridWorld.git
    cd HackerGridWorld
    conda env create -f conda-environment.yml
    conda activate HGW
    # Start server and client in different consoles, or use tmux
    tmux new-session -d -s HGW-server 'python server.py -c HGW.server.conf'

## Play as human

    python ./client.py

## Train a q-learning reinforcement learning agent

    python ./agent.py

# Rules of the game

- The world is a 2D grid of X times Y. Defined by the configuration of the server (` HGW.server.conf`)
- The world has two ways to end:
    - Score is 0
    - You stepped into the output gate square
- The score starts by some predefined value in the server's configuration. But I suggest to make it large so you give time to your agent to spend a lot of steps randomly learning.
- The output gate (marked by default by an O in the world) increments your score and ends the game.
- There can be objects in the world (such as a treasure with money marked by the X), that increment or decrement your score. You need to find out by yourself.
- The goal is to finish the game with the maximum amount of score.
- There are 4 possible actions: up, down, left, right.
- If you try to move outside the grid, you will stay in the last valid position of the grid. 
- Every action taken has a penalty of -1 in the score. If you keep moving outside the grid with actions, even if your position does not change, you are penalized.

# Why remote server as a game environment
The idea of having a world in as TCP server is to have this features:
- It forces you NOT to control the server completely, maybe is on the cloud, part of a CTF, or controlled by someone else. The idea is that it is an unknown world for you. Your code doesn't have to, and can not control, modify or change the server. 
- It allows a complete separation of the world itself and how you want to solve it, you can play as human, bot, or as any algorithm.
- You can connect many clients/agents simultaneously to the game.
- You can also ask to reply any strategy since the world doesn't care who plays or how they play.
- The world is slower than an in-memory environment, yes. So probably strategies need to adapt.

# Communication with clients/agents and actions
The server gives a new _fresh_ world as a JSON to any client connecting. The JSON has the following parts:

    {"size_x": 10, 
    "size_y": 10, 
    "min_x": 0, 
    "min_y": 0, 
    "max_x": 9, 
    "max_y": 9, 
    "size": "10x10", 
    "score": 692, 
    "positions": [" ", " ", " ", " ", " ", " ", " ", " ", " ", "X", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "
    ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "
    ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "
    ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "O"], 
    "current_character_position": 99, 
    "end": true}

The size is sent in several forms, but that will probably change to one later. You also have the min and max positions in both axes so you know the shape of the world, but that will probably change too.

When the game ends the property "end" will be true, otherwise it is false.

In every step, the server sends a new JSON with the current state to the client.

## Actions
After each world is sent, the server listens for actions back. The actions should be a single string of text. The current available actions are:

- 'UP': To go up
- 'DOWN': To go down
- 'LEFT': To go left
- 'RIGHT': To go right


# Visualization

The client and agent automatically visualize the world and the actions using curses in the terminal. This makes then slower but it is really nice to see which actions they are taking and how all the actions look like in the real game. You can see how the actions of the agent start to make sense more and more.


# Logs

The server, client and agent create logs called `server.log`, `client.log`, and `agent.log`. The verbosity can be controlled. Be careful because using logging.INFO for the agent can lead to a log of hundreds of megabytes in a couple of minutes. By default they use logging.ERROR.

# Monitoring
The best way to monitor now the progress is 

    tail -f agent.log

# Final strategy and Replay
The strategy of the current agent is the generated q-table. The strategy with the best score is automatically saved in a file called `best-model.npy` (numpy array) and `best-model.txt` (text file of the qtable for you to analyze). 

You can __replay__ and watch the saved strategies back, to see what your model learned. For this you need:

A new server running with speed 0.1. Put in the configuration of the server (`HGW.server.conf`)

    "speed": 0.1,
    
And change the port so you just dont collide with the training server:

    "port": 9001,

Then run the command:

    python agent.py -c HGW.agent-qlearning.conf -r best-model.npy

The configuration is technically not necessary to replay, but now it is mandatory to have one so...


# Files

- HGW.agent-qlearning.conf: Configuration of the agent
- HGW.server.conf: Configuration of the server
- agent.py: Code of the learning agent
- client.py: Code of the human client to play
- server.py: Code of the server

# What happened to the emojis in the console?

The curses library really doesn't like the varying width of emojis, so it keep breaking the terminal and making impossible to see correctly. So I went back to ASCII :-(

# How playing the client looks like
<p align="center">
<img src="https://github.com/stratosphereips/HackerGridWorld/raw/main/client.gif" width="450px" title="HGW in action.">
</p>
