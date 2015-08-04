#!/usr/bin/python

# roshambono.py -- console harness

HELP = '''\
usage:

    To play a game to 1000 between p_rock and p_random:

        $ python roshambono.py play 1000 p_rock p_random

    To play a round robin tourney for 100 games to 1000 between p_rock and p_paper and p_random: 

        $ python roshambono.py tourney 100 1000 p_rock p_paper p_random
'''

import sys
import imp
import logging
import random
import time

# ignore SIG_PIPE
from signal import (signal,SIGPIPE,SIG_DFL)

signal(SIGPIPE, SIG_DFL)


ROCK        = 1
PAPER       = 2
SCISSORS    = 3

BEATS       = [0,3,1,2]
BEAT_BY     = [0,2,3,1]

def get_play(f_get_play,state,catch_exceptions) :
    play = 0
    try :
        play = int(f_get_play(state))
    except KeyboardInterrupt :
        raise
    except :
        if not catch_exceptions :
            raise
        logging.warn('caught exception "%s" calling %s \'s get_play() function' % (sys.exc_info()[1],str(f_get_play)))
    if play < 1 or play > 3 :
        play = random.randint(1,3)
    logging.debug('LOG_PLAY\t%d\t%d\t%s' % (state,play,str(f_get_play)))
    return play

def play_game(race_to,f_get_play_a,f_get_play_b,catch_exceptions) :
    wins = [0,0]
    plays = [[-1,0,0,0],[-1,0,0,0]]
    last_a = last_b = 0
    while 1 :
        a_play = get_play(f_get_play_a,last_a,catch_exceptions)
        b_play = get_play(f_get_play_b,last_b,catch_exceptions)
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

def split_playername(playername) :
    parts = playername.split(':')
    if 1 == len(parts) :
        return (parts[0],parts[0],'player','get_play')
    if 2 == len(parts) :
        return (parts[0],parts[1],'player','get_play')
    if 3 == len(parts) :
        return (parts[0],parts[1],parts[2],'get_play')
    if 4 == len(parts) :
        return (parts[0],parts[1],parts[2],parts[3])
    raise Exception('i don\'t know how to parse "%s"' % playername)

def make_player(playername,catch_exceptions) :
    name,path,modulename,attr = split_playername(playername)
    fp = pathname = description = m = None
    try :
        fp,pathname,description = imp.find_module(modulename,[path,])
    except :
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" finding module %s' % (sys.exc_info()[1],modulename))
    try :
        if fp :
            m = imp.load_module(playername,fp,pathname,description)
    except :
        if not catch_exceptions:
            raise
        logging.warn('caught exception "%s" importing %s' % (sys.exc_info()[1],playername))
    finally :
        if fp :
            fp.close()
    if None == m :
        return None
    f = getattr(m,attr)
    return f

def play_tourney(t,n,playernames) :
    scores = {}
    players = []
    for i in playernames :
        f = make_player(i,True)
        scores[len(players)] = 0
        players.append(f)
    for r in range(t) :
        for i in range(len(players)) :
            for j in range(len(players)) :
                if i >= j :
                    continue
                x = play_game(n,players[i],players[j],True)
                if 0 == x :
                    scores[i] += 1
                else :
                    scores[j] += 1
                logging.info('SCORE\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s' % (r,t,i,j,scores[i],scores[j],playernames[i],playernames[j]))
        logging.info('STATUS\t%.2f\t\t%s' % (r/float(t),','.join(map(lambda i : '%s:%s' % (playernames[i],scores[i]),range(len(players))))))
    logging.info('STATUS\t%.2f\t\t%s' % (100.0,','.join(map(lambda i : '%s:%s' % (playernames[i],scores[i]),range(len(players))))))
    return -1

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
        logging.basicConfig(level=logging.DEBUG,format='%(message)s',stream=sys.stdout)
        n = int(sys.argv[2])
        a_player = make_player(argv[3],False)
        b_player = make_player(argv[4],False)
        x = play_game(n,a_player,b_player,False)
        return x
  
    elif 'tourney' == c :
        logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)-7s %(message)s',stream=sys.stdout)
        t = int(sys.argv[2])
        n = int(sys.argv[3])
        playernames = sys.argv[4:]
        x = play_tourney(t,n,playernames)
        return x
    
    else :
        logging.error('i don\'t know how to "%s". look at the source' % c)
        print HELP
        sys.exit()

if __name__ == '__main__' :
    main(sys.argv)

