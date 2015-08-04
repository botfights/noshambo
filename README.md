Noshambo
========

Noshambo is roshambo (or Rock-Paper-Scissors) with no ties.

Rock beats scissors, scissors beats paper, paper beats rock.

However, if there are is a tie, the player who has played that shape
more often wins. If each player has played that shape the same number 
of times, then the player who has played the shape that beats it more
wins. If still tied, then a coin is tossed.

For example, if both players play "Rock", then the player who
has played "Rock" more often wins. If both players have played 
"Rock" the same amount of times, she who played "Paper" more wins.

You can write a robot by implementing the get\_play() function in 
p\_robot/bot.py:

    def get_play(state) 
        
        return 1 for Rock, 2 for Paper, and 3 for Scissors.
    
        state is an 8 bit unsigned integer representing the
        result of the last hand. 

        if it is 0, it is the first game. 

        otherwise, bits 0 and 1 represent your move,
        bits 2 and 3 represent your opponent's move, 
        bits 4 and 5 represent the number of tiebreakers
        needed to resolve the game, and 
        bit 6 is set if you won, or 0 if you lost.

        for example, if in the last game you played Rock,
        and your opponent played Scissors, state would be:

        (1) | (3 << 2) | (0 << 4) | (1 << 6) = 77

To play first to 100 rock against random:

    $ git clone https://github.com/botfights/noshambo.git
    $ cd noshambo
    $ python noshambo.py play 100 p_rock p_random

Next, edit p\_robot/bot.py, implement play(), then play your
robot against the random:

    $ python noshambo.py play 100 p_robot p_random

To play a round robin tournament of 100 games each to 1000:

    $ python noshambo.py tournament 100 1000 p_robot p_random p_rock

Have fun!

