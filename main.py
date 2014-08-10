#!/usr/bin/python

# main.py -- console harness

HELP = '''\
usage:

    To play a game to 1000 between p_rock and p_random:

        $ python main.py play 1000 p_rock p_random

    To play a round robin tourney for 100 games to 1000 between p_rock and p_paper and p_random: 

        $ python main.py tourney 100 1000 p_rock p_paper p_random
'''

import sys
import imp
import logging
import random
import time

import roshambo

# ignore SIG_PIPE
from signal import (signal,
                    SIGPIPE,
                    SIG_DFL)

signal(SIGPIPE, SIG_DFL)


def split_playername(playername):
    parts = playername.split(':')
    if 1 == len(parts):
        return (parts[0],parts[0],'player','get_play')
    if 2 == len(parts):
        return (parts[0],parts[1],'player','get_play')
    if 3 == len(parts):
        return (parts[0],parts[1],parts[2],'get_play')
    if 4 == len(parts):
        return (parts[0],parts[1],parts[2],parts[3])
    raise Exception('i don\'t know how to parse "%s"' % playername)

def make_player(playername, path, modulename, attr, catch_exceptions):
    fp = pathname = description = m = None
    try:
        fp, pathname, description = imp.find_module(modulename, [path,])
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" finding module %s' % (sys.exc_info()[1],modulename))
 
    try:
        if fp:
            m = imp.load_module(playername, fp, pathname, description)
    except:
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" importing %s' % (sys.exc_info()[1],playername))
    finally:
        if fp:
            fp.close()

    if None == m :
        return None

    f = getattr(m, attr)
    return f


def play_games(n,seed,playernames,catch_exceptions) :
    random.seed(seed)
    logging.debug('SEED\t%s' % seed)
    players = {}
    scores = {}
    names = {}
    for i in playernames :
        playername, path, modulename, attr = split_playername(i)
        logging.info('playername: %s => %s' % (i,split_playername(i)))
        player_id = chr(ord('A') + len(players))
        names[player_id] = playername
        logging.info('making player %s (%s) ...' % (player_id,playername))
        p = make_player(playername, path, modulename, attr, catch_exceptions)
        players[player_id] = p
        scores[player_id] = 0
    game_num = 0
    for r in range(n) :
        game_num += 1
        logging.debug('playing game %d ...' % (game_num,))
        winner = liarsdice.play_game(game_num,players,names,catch_exceptions)
        scores[winner] += 1
        logging.debug('RESULT\tgame:%d\twinner:%s' % (game_num,winner))
        k = scores.keys()
        k.sort(key = lambda x : scores[x],reverse = True)
        rank = 0
        for i in k :
            rank += 1
            logging.info('SCORE\tgame %d of %d\t#%d.\t%s\t%s\t%d' % (game_num,n,rank,i,names[i],scores[i]))
        logging.info('SCORE')
        logging.info('STATUS\t%.2f\t\t%s' % (game_num/float(n),','.join(map(lambda i : '%s:%s' % (names[i],scores[i]),k))))
    return scores

def main(argv) :
    if 1 == len(argv) :
        print HELP
        sys.exit()

    c = argv[1]

    if 0 :
        pass

    elif 'help' == c :
        print HELP
        sys.exit()

    elif 'play' == c :
        logging.basicConfig(level=logging.INFO,format='%(message)s',stream=sys.stdout)
        n = 1
        player_names = sys.argv[2:]
        seed = int(time.time() * 1000)
        play_games(n,seed,player_names,False)
  
    elif 'tournament' == c :
        logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)-7s %(message)s',stream=sys.stdout)
        n = int(sys.argv[2])
        player_names = sys.argv[3:]
        seed = ''.join(sys.argv)
        play_games(n,seed,player_names,True)
    
    else :
        logging.error('i don\'t know how to "%s". look at the source' % c)
        print HELP
        sys.exit()

if __name__ == '__main__' :
    main(sys.argv)

