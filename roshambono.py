# roshambono.py

def get_play(game_id,hand_num,who,f_get_play,player_name,hands_str,history_str,catch_exceptions) :
    play = 0
    try :
        play = int(f_get_play(who,hands_str,history_str))
    except KeyboardInterrupt :
        raise
    except :
        if not catch_exceptions :
            raise
        logging.warn('caught exception "%s" calling %s (%s) \'s get_play() function' % (sys.exc_info()[1],who,player_name))
    logging.debug('LOG_PLAY\tG%sH%d\t%s-%s\t%s\t%s\t%d' % (game_id,hand_num,who,player_name,hands_str,history_str,play))
    return play

def play_game(game_id,players,player_names,catch_exceptions) :
    
    # first, set up the players left in the game
    #
    seats = players.keys()
    seats.sort()
    random.shuffle(seats)
    whose_move = 0
    cups = {}
    dice = RULES_DICE
    faces = RULES_FACES
    for i in seats :
        cups[i] = dice

    logging.info('=' * 50)
    logging.info('new game between %s' % ', '.join(map(lambda x : '%s-%s' % (x,player_names[x]),seats)))

    # keep playing hands until only one player left
    #
    hand_num = 0
    while 1 :
        hand_num += 1

        # only one player left?
        #
        winner = None
        for i in seats :
            if 0 != cups[i] :
                if None != winner :
                    winner = None
                    break
                winner = i
        if None != winner :
            break

        # everyone rolls their dice
        #
        logging.info('-' * 50)
        logging.info('new hand between %s with %s dice, respectfully' % (', '.join(map(lambda x : '%s-%s' % (x,player_names[x]),filter(lambda x : 0 != cups[x],seats))),', '.join(map(lambda x : '%d' % cups[x],filter(lambda x : 0 != cups[x],seats)))))
        hands = {}
        for i in seats :
            if 0 == cups[i] :
                continue
            hands[i] = []
            logging.debug('rolling %d dice for %s ...' % (cups[i],i))
            for j in range(cups[i]) :
                hands[i].append(random.randint(1,faces))
            hands[i].sort(reverse=True)

        logging.debug('hands: %s' % str(filter(lambda x : 0 != cups[x[0]],hands.items())))
        
        # keep playing hands until someone calls liar
        #
        history = []
        while 1 :
            
            logging.debug('getting move from %s ...' % seats[whose_move])

            # build history
            #
            history_str = ','.join(map(lambda x : '%s:%d' % (seats[x[0]],x[1]),history))

            # build hands
            #
            hands_str = None
            for i in seats :
                if None == hands_str :
                    hands_str = ''
                else :
                    hands_str += ','
                if i == seats[whose_move] :
                    hands_str += '%s:%s' % (seats[whose_move],''.join(map(lambda x : str(x),hands[seats[whose_move]])))
                else :
                    hands_str += '%s:%s' % (i,'x' * cups[i])

            # get the play
            #
            play = get_play(game_id,hand_num,seats[whose_move],players[seats[whose_move]],player_names[seats[whose_move]],hands_str,history_str,catch_exceptions)
            logging.info('player %s calls "%s"' % (seats[whose_move],verbose_play(play)))

            # check for legal moves
            # 
            if 0 != play :
                face = play % 10
                quantity = play // 10
                if face <= 0 or face > faces or quantity <= 0 or quantity > (len(players) * dice) :
                    logging.info('illegal move, assuming calling liar')
                    play = 0
                elif 0 != len(history) :
                    last_play = history[-1][1]
                    last_face = last_play % 10
                    last_quantity = last_play // 10
                    if (quantity < last_quantity) or ((quantity == last_quantity) and (face <= last_face)) :
                        logging.info('not increasing play, assuming calling liar')
                        play = 0

            # remember the play
            #
            history.append((whose_move,play))
            
            # if it's a call, or an illegal move, or a bet less than the last play
            # treat it as a call and check the bluff
            #
            loser = None
            result = None
            if 0 == play :
                
                # if it's the first play, they lose
                #
                if 1 == len(history) :
                    logging.debug('called liar before any plays')
                    loser = seats[whose_move]
                    result = 1

                else :
                    
                    # count dice
                    #
                    common_dice = {}
                    for i in seats :
                        if 0 == cups[i] :
                            continue
                        for j in hands[i] :
                            common_dice[j] = common_dice.get(j,0) + 1
 
                    last_play = history[-2][1]
                    last_face = last_play % 10
                    last_quantity = last_play // 10
 
                    logging.debug('hands: %s' % str(hands))
                    logging.debug('common dice: %s' % str(common_dice))

                    logging.info('player %s-%s calls liar on player %s-%s\'s call of %s' % (seats[whose_move],player_names[seats[whose_move]],seats[history[-2][0]],player_names[seats[history[-2][0]]],verbose_play(last_play)))
                    logging.info('hands: %s' % ', '.join(map(lambda x : '%s:%s' % (x,''.join(map(lambda y : str(y),hands[x]))),filter(lambda x : 0 != cups[x],seats))))
                    logging.info('common dice: %s' % ', '.join(map(lambda x : verbose_play((x[1] * 10) + x[0]),common_dice.items())))

                    if common_dice.get(last_face,0) >= last_quantity :
                        logging.debug('%s\'s last play was %d %d\'s, CORRECT, %s loses' % (seats[history[-2][0]],last_quantity,last_face,seats[whose_move]))
                        loser = seats[whose_move]
                        result = 2
                    else :
                        logging.debug('%s\'s last play was %d %d\'s, INCORRECT, %s loses' % (seats[history[-2][0]],last_quantity,last_face,seats[history[-2][0]]))
                        loser = seats[history[-2][0]]
                        result = 3

                # remove loser's die, bump them if they're out of dice,
                # and start over again
                #
                # show everyone the result
                #
                logging.debug('showing everyone the result')
                history_str = ','.join(map(lambda x : '%s:%d' % (seats[x[0]],x[1]),history))
                hands_str = ','.join(map(lambda x : '%s:%s' % (x,''.join(map(lambda y : str(y),hands[x]))),filter(lambda x : 0 != cups[x],seats)))
                logging.debug('LOG_HAND\tG%sH%d\t%s\t%s\tLOSER:%s-%s\t%d' % (game_id,hand_num,hands_str,history_str,loser,player_names[loser],result))
                logging.info('player %s-%s loses one die' % (loser,player_names[loser]))
                cups[loser] -= 1
                if 0 == cups[loser] :
                    logging.info('player %s-%s has no dice left' % (loser,player_names[loser]))
                for i in seats :
                    get_play(game_id,hand_num,i,players[i],player_names[i],hands_str,history_str,catch_exceptions)
              
            # advance next move
            #
            while 1 :
                whose_move += 1
                if whose_move == len(seats) :
                    whose_move = 0
                if 0 != cups[seats[whose_move]] :
                    break

            # new hand if necessary
            #
            if None != loser :
                break

    logging.debug('LOG_GAME\t%s\t%s' % (game_id,winner))
    logging.info('player %s-%s wins' % (winner,player_names[winner]))
    return winner

