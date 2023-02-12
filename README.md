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

# Visualization

The client and agent automatically visualize the world and the actions using curses in the terminal. This makes then slower but it is really nice to see which actions they are taking and how all the actions look like in the real game. You can see how the actions of the agent start to make sense more and more.

# Logs

The server, client and agent create logs called `server.log`, `client.log`, and `agent.log`. The verbosity can be controlled. Be careful because using logging.INFO for the agent can lead to a log of hundreds of megabytes in a couple of minutes. By default they use logging.ERROR.

# What happened to the emojis in the console?

The curses library really doesn't like the varying width of emojis, so it keep breaking the terminal and making impossible to see correctly. So I went back to ASCII :-(

# How playing the client looks like
<p align="center">
<img src="https://github.com/stratosphereips/HackerGridWorld/raw/main/client.gif" width="450px" title="HGW in action.">
</p>
