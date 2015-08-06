#!/usr/bin/python

# noshambo.py -- console harness

import sys
import imp
import logging
import random
import time
import getopt

# ignore SIG_PIPE
from signal import (signal,SIGPIPE,SIG_DFL)

signal(SIGPIPE, SIG_DFL)


ROCK        = 1
PAPER       = 2
SCISSORS    = 3

BEATS       = [0,3,1,2]
BEAT_BY     = [0,2,3,1]


def get_play(player, my_id, her_id, last):
    x = None
    try:
        x = player.get_play(my_id, her_id, last)
    except:
        pass
    if not x in (1, 2, 3):
        x = random.choice((1, 2, 3))
    return x


def play_game(race_to, player1, player2):
    wins = [0,0]
    plays = [[-1,0,0,0],[-1,0,0,0]]
    last_a = last_b = 0
    while 1 :
        a_play = get_play(player1, player1.player_id, player2.player_id, last_a)
        b_play = get_play(player2, player2.player_id, player1.player_id, last_b)
        ties = 0
        if a_play == b_play :
            ties += 1
            x = plays[0][a_play] - plays[1][b_play]
            if 0 == x :
                ties += 1
                x = plays[0][BEAT_BY[a_play]] - plays[1][BEAT_BY[b_play]]
                if 0 == x :
                    ties += 1
                    a_won = random.randint(0,1)
                elif 0 > x :
                    a_won = 0
                else :
                    a_won = 1
            elif 0 > x :
                a_won = 0
            else :
                a_won = 1
        else :
            a_won = 1
            if BEATS[b_play] == a_play :
                a_won = 0
        plays[0][a_play] += 1
        plays[1][b_play] += 1
        last_a = a_play | (b_play << 2) | (ties << 4) | (a_won << 6)
        last_b = b_play | (a_play << 2) | (ties << 4) | ((1 - a_won) << 6)
        if a_won :
            wins[0] += 1
        else :
            wins[1] += 1
        logging.debug('GAME\t%d\t%d\t%d\t%d\t%d' % (wins[0],wins[1],a_play,b_play,a_won))
        if wins[0] == race_to :
            return 0
        if wins[1] == race_to :
            return 1

def play_tournament(t, n, players) :
    scores = {}
    for i in range(len(players)):
        scores[i] = 0
    for r in range(t) :
        for i in range(len(players)) :
            for j in range(len(players)) :
                if i >= j :
                    continue
                x = play_game(n, players[i], players[j])
                if 0 == x :
                    scores[i] += 1
                else :
                    scores[j] += 1
                logging.info('SCORE\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s' % (r,t,i,j,scores[i],scores[j],players[i].playername,players[j].playername))
        logging.info('BOTFIGHTS\t%.2f\t\t%s' % (r/float(t),','.join(map(lambda i : '%s:%s' % (players[i].playername,scores[i]),range(len(players))))))
    logging.info('BOTFIGHTS\t%.2f\t\t%s' % (100.0,','.join(map(lambda i : '%s:%s' % (players[i].playername,scores[i]),range(len(players))))))
    return -1


class Player():
    pass


def call_player(player, args, default):
    global g_catch_exceptions
    result = default
    start = time.clock()
    try:
        result = player.play(*args)
    except KeyboardInterrupt:
        raise
    except:
        logging.warn('caught exception "%s" calling %s (%s)'
                     % (sys.exc_info()[1], player.player_id, player.playername))
        if not g_catch_exceptions:
            raise
    elapsed = time.clock() - start
    player.elapsed += elapsed
    player.calls += 1
    return result


def make_player(player_id, dirname):
    global g_catch_exceptions
    m = None
    try:
        name = 'bot'
        (f, filename, data) = imp.find_module(name, [dirname, ])
        m = imp.load_module(name, f, filename, data)
    except:
        logging.error('caught exception "%s" loading %s' % \
                      (sys.exc_info()[1], dirname))
        if not g_catch_exceptions:
            raise
    p = Player()
    p.player_id = player_id
    p.playername = dirname
    z = p.playername.rfind('/')
    if -1 != z:
        p.playername = p.playername[z + 1:]
    p.play = None
    if None == m or not hasattr(m, 'play'):
        logging.error('%s has no function "play"; ignoring ...' % dirname)
    else:
        p.play = getattr(m, 'play')
    p.elapsed = 0.0
    p.calls = 0
    p.get_play = lambda x, y, z: call_player(p, (x, y, z), random.choice((1, 2, 3)))
    return p


def usage():
    print('''\
noshambo! see: http://github.com/botfights/noshambo for dox

usage:

    $ python noshambo.py <command> [<option> ...] [<arg> ...]

commands:

    game [<player1>] [<player2>] ...

                        play a single game between players

    tournament [<player1>] [<player2>] ...

                        play a tournament between players
options:

    -h, --help                      show this help
    --seed=<s>                      set seed for random number generator
    --catch-exceptions=<off|on>     catch and log exceptions
    --race-to=<n>                   set number of hands to play per game (defaults to 100)
    --num-games=<n>                 set number of games for tournament (defaults to 100)

    --log-level=<n>                 set log level (10 debug, 20 info, 40 error)
''')


def main(argv):
    if 1 > len(argv):
        usage()
        sys.exit()
    command = argv[0]
    try:
        opts, args = getopt.getopt(argv[1:], "h", [
                                                    "help",
                                                    "seed=",
                                                    "catch-exceptions=",
                                                    "num-games=",
                                                    "race-to=",
                                                    "log-level=",
                                                    ])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(1)
    seed = time.time()
    num_games = 100
    race_to = 100
    log_level = logging.DEBUG
    global g_catch_exceptions
    g_catch_exceptions = False
    for o, a in opts:
        if 0:
            pass
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("--seed", ):
            seed = a
        elif o in ("--num-games", ):
            num_games = int(a)
        elif o in ("--race-to", ):
            race_to = int(a)
        elif o in ("--log-level", ):
            log_level = int(a)
        elif o in ("--catch-exceptions", ):
            g_catch_exceptions = 'off' != a
        else:
            raise Exception("unhandled option")
    random.seed(seed)

    if 0:
        pass

    elif 'game' == command:
        logging.basicConfig(level=log_level, format='%(message)s', 
                        stream=sys.stdout)
        player1 = make_player('a', args[0])
        player2 = make_player('b', args[1])
        winner = play_game(race_to, player1, player2)
        sys.exit()

    elif 'tournament' == command:
        logging.basicConfig(level=log_level, format='%(message)s', 
                        stream=sys.stdout)
        players = []
        for player_id, playername in enumerate(args):
            players.append(make_player(chr(ord('a') + player_id), playername))
        play_tournament(race_to, num_games, players)
        sys.exit()

    else:
        print 'i don\'t know how to "%s".' % command
        usage()
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
