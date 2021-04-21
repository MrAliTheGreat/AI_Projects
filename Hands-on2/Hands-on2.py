import random
import copy
import time

class Player:
    def __init__(self, name, num_of_cards):
        """
        The base player class of the game
        Inputs
        -----------
        name = (str) player's name
        num_of_cards = (int) number of cards in the deck
        """
        self.name = name
        self.deck_count = num_of_cards
        self.target = self.deck_count * 2 - 1
        self.cards = []
        self.erases_remaining = self.deck_count // 5
        self.has_stopped = False

    def draw_card(self, card):
        """
        draws a card, and adds it to player cards
        Input
        -------------
        card: (int) the card to be added
        """
        self.cards.append(card)

    def print_info(self):
        """
        prints info of the player
        """
        print(f"{self.name}'s cards: ", end='')
        for c in self.cards:
            print(f'{c}, ', end='')
        print(f'sum: {sum(self.cards)}')
    
    def get_margin(self):
        """
        returns the margin left to target by the player
        Output
        ----------
        (int) margin to target
        """
        return self.target - sum(self.cards)
    
    def cpu_play(self, seen_cards, deck, enemies_cards):
        """
        The function for cpu to play the game
        Inputs
        ----------
        seen_cards:     (list of ints) the cards that have been seen until now
        deck:           (list of ints) the remaining playing deck of the game
        enemies_cards:  (list of ints) the cards that the enemy currently has.
        Output
        ----------
        (str) a command given to the game
        
        """
        if (len(deck) > 0):
            next_card_in_deck = deck[0]
        else:
            next_card_in_deck = 0
        if (len(deck) > 1):
            next_enemy_card_in_deck = deck[1]
        else:
            next_enemy_card_in_deck = 0
        amount_to_target = self.target - sum(self.cards)
        amount_with_next_card = self.target - (sum(self.cards) + next_card_in_deck)
        enemies_amount_to_target = self.target - sum(enemies_cards)
        enemies_amount_with_next_card = self.target - (sum(enemies_cards) + next_enemy_card_in_deck)
        _stop_condition = amount_to_target < next_card_in_deck and self.erases_remaining <= 0
        _draw_condition_1 = next_card_in_deck != 0
        _draw_condition_2 = amount_with_next_card >= 0
        _erase_condition = self.erases_remaining > 0
        _erase_self_condition = amount_to_target < 0
        _erase_opponent_condition_or = enemies_amount_to_target < (self.target // 7)
        _erase_opponent_condition_or_2 = enemies_amount_with_next_card < (self.target // 7) 
        _erase_opponent_condition_or_3 = enemies_amount_with_next_card <= amount_with_next_card
        _erase_opponent_condition_or_4 = enemies_amount_to_target <= amount_to_target
        _erase_opponent_condition = _erase_opponent_condition_or or _erase_opponent_condition_or_2 or _erase_opponent_condition_or_3
        _erase_opponent_condition = _erase_opponent_condition or _erase_opponent_condition_or_4 
        if (_stop_condition):
            return 'stop'
        elif (_draw_condition_1 and _draw_condition_2):
            return 'draw'
        elif(_erase_self_condition and _erase_condition):
            return 'erase_self'
        elif(_erase_opponent_condition and _erase_condition):
            return 'erase_opponent'
        else:
            return 'stop'
    
    def erase(self, target):
        """
        erases the last card of the target
        Input
        ---------
        target: (Player obj) the player whos last card is about to be erased
        """
        if (len(target.cards) == 0):
            # print(f'{target.name} has no more eraseble cards!')
            return
        if (self.erases_remaining > 0):
            self.erases_remaining -= 1
            card = target.cards.pop(-1)
            # print(f'{self.name} erased {card} from {target.name}\'s deck!')
            return
        # print(f'{self.name} has no more erases remaining!')

    def get_player_cards(self):
        return self.cards

    def get_erases_remained(self):
        return self.erases_remaining


class Blacksin:
    def __init__(self, deck_count=21):
        """
        The main game class
        Inputs
        -----------
        deck_count = (int) number of cards in the deck
        """
        self.deck_count = deck_count
        self.target = self.deck_count * 2 - 1
        self.player = Player('player', deck_count)
        self.opponent = Player('opponent', deck_count)
        self.deck = self.shuffle_cards()
        self.seen_cards = []
    
    def shuffle_cards(self):
        """ 
        shuffles cards for deck creation
        """
        return list(random.sample(range(1, self.deck_count + 1), self.deck_count))

    def draw_card(self):
        """ 
        draws a card from deck, if non is remaining, ends the game.
        """
        if (len(self.deck) > 0):
            card = self.deck.pop(0)
            self.seen_cards.append(card)
            return card
        # print('The deck is empty! ending game...')
        self.opponent.has_stopped = True
        self.player.has_stopped = True
        return -1

    def handout_cards(self):
        """ 
        hands out cards to players
        """
        self.player.draw_card(self.draw_card())
        self.opponent.draw_card(self.draw_card())
        self.player.draw_card(self.draw_card())
        self.opponent.draw_card(self.draw_card())
    
    def handle_input(self, _input, player):
        """ 
        handles input
        Input
        ------------
        _input: (str) input given by the player
        player: (Player obj)the player that is giving the input
        
        """
        if (player is self.player):
            opponent = self.opponent
        else:
            opponent = self.player
        if (_input == 'stop' or _input == 's'):
            player.has_stopped = True
            # print(f'{player.name} has stopped')
        elif (_input == 'draw' or _input == 'd'):
            card = self.draw_card()
            if (card == -1): return True
            player.draw_card(card)
            # print(f'{player.name} drawed a card: {card}')
        elif ((_input == 'erase_self' or _input == 'es')):
            player.erase(player)
        elif ((_input == 'erase_opponent' or _input == 'eo')):
            player.erase(opponent)
        else:
            # print('ERROR: unknown command')
            return False
        return True

    def get_player_input(self):
        minimaxTree = MinimaxTree()
        root = MinimaxNode(self.player , self.opponent , self.deck)

        # player_input = minimaxTree.minimax(root)
        player_input = minimaxTree.minimaxWithPruning(root , float("-inf") , float("inf"))

        self.handle_input(player_input , self.player)        
            
    def opponent_play(self):
        """
        function for opponent to play it's turn
        """
        try:
            opponent_input = self.opponent.cpu_play(self.seen_cards, self.deck, self.player.cards)
        except:
            opponent_input = 'stop'

        self.handle_input(opponent_input, self.opponent)

    def check_for_winners(self):
        """
        checks for winners.
        Output
        -----------
        (int) returns 1 if player wins, 0 if draw and -1 if opponent wins
        """
        # self.opponent.print_info()
        # self.player.print_info()
        player_margin = self.player.get_margin()
        opponent_margin = self.opponent.get_margin()
        player_win_condition_1 = opponent_margin < 0 and player_margin >= 0
        player_win_condition_2 = opponent_margin >=0 and player_margin >= 0 and player_margin < opponent_margin
        draw_condition_1 = opponent_margin < 0 and player_margin < 0
        draw_condition_2 = opponent_margin >= 0 and player_margin >= 0 and player_margin == opponent_margin
        opponent_win_condition_1 = player_margin < 0 and opponent_margin >= 0
        opponent_win_condition_2 = opponent_margin >=0 and player_margin >= 0 and player_margin > opponent_margin
        if (player_win_condition_1 or player_win_condition_2):
            # print(f'the winner is the {self.player.name}!')
            return 1
        elif(draw_condition_1 or draw_condition_2):
            # print('the game ends in a draw!')
            return 0
        elif(opponent_win_condition_1 or opponent_win_condition_2):
            # print(f'the winner is the {self.opponent.name}!')
            return -1
        else:
            # print('an error has accurred! exiting...')
            exit()

    def print_deck(self):
        """
        prints the current deck of the game
        """
        print('full deck: [top] ', end='')
        for i in self.deck:
            print(i, end=' ')
        print('[bottom]')

    def run(self):
        """
        main function to run the game with
        """
        # print('\nstarting game... shuffling... handing out cards...')
        # print(f'remember, you are aiming for nearest to: {self.target}')
        # self.print_deck()
        self.handout_cards()
        turn = 0
        while(not self.player.has_stopped or not self.opponent.has_stopped):
            if (turn == 0):
                if (not self.player.has_stopped):
                    # self.player.print_info()
                    # self.opponent.print_info()
                    self.get_player_input()
                    # print()
            else:
                if (not self.opponent.has_stopped):
                    # print('opponent playing...')
                    self.opponent_play()
                    # print()
            turn = 1 - turn
        # print('\nand the winner is...')
        return self.check_for_winners()



class MinimaxNode():
    def __init__(self, player , opponent , deck):
        self.player = player
        self.opponent = opponent
        self.deck = deck


class MinimaxTree():
    def __init__(self):
        self.maxDepth = 6
        self.playerDistRatio = 10
        self.playerErasesRatio = 0
        self.opponentDistRatio = 0.1
        self.opponentErasesRatio = 20


    def drawCard(self , node):
        if (len(node.deck) > 0):
            card = node.deck.pop(0)
            return card

        node.opponent.has_stopped = True
        node.player.has_stopped = True
        return -1


    def makeNewNodeByMove(self , node , move , turn):
        if (turn == "player"):
            player = node.player
            opponent = node.opponent
        else:
            player = node.opponent
            opponent = node.player

        if (move == 's'):            
            player.has_stopped = True
        
        elif (move == 'd'):
            if(player.has_stopped):
                return None
            
            card = self.drawCard(node)
            if (card == -1): return node
            player.draw_card(card)
        
        elif (move == 'es'):
            if(len(player.cards) == 0 or player.erases_remaining <= 0 or player.has_stopped):
                return None
            
            player.erase(player)
        
        elif (move == 'eo'):
            if(len(opponent.cards) == 0 or player.erases_remaining <= 0 or player.has_stopped):
                return None
            
            player.erase(opponent)
        
        else:
            return None
        
        return node


    def evaluateFunction(self , node):
        playerValue = sum(node.player.cards)
        if(playerValue == 41):
            return 10 ** 10
        elif(playerValue > 41):
            playerValue = 41 - playerValue

        opponentValue = sum(node.opponent.cards)
        if(opponentValue == 41):
            return -10 ** 10
        elif(opponentValue > 41):
            opponentValue = 41 - opponentValue

        return (self.playerDistRatio * playerValue + self.playerErasesRatio * node.player.erases_remaining) - \
               (self.opponentDistRatio * opponentValue + self.opponentErasesRatio * node.opponent.erases_remaining)    

    
    def minimax(self , currentNode , depth=0):
        moves = ["s" , "d" , "es" , "eo"]

        if(depth > self.maxDepth or (currentNode.player.has_stopped and currentNode.opponent.has_stopped)):
            return self.evaluateFunction(currentNode)

        
        if(depth % 2 == 0):  # Player: Maximize
            maxTotal = float("-inf")
            for move in moves:
                newNode = self.makeNewNodeByMove(copy.deepcopy(currentNode) , move , "player")
                if(newNode is None):
                    continue

                moveValue = self.minimax(newNode , depth + 1)
                if(moveValue > maxTotal):
                    maxTotal = moveValue
                    bestMove = move

            if(depth == 0):
                return bestMove
            else:
                return maxTotal

        else:  # Opponent: Minimize
            minTotal = float("inf")
            for move in moves:
                newNode = self.makeNewNodeByMove(copy.deepcopy(currentNode) , move , "opponent")              
                if(newNode is None):
                    continue

                moveValue = self.minimax(newNode , depth + 1)
                if(moveValue < minTotal):
                    minTotal = moveValue

            return minTotal


    def minimaxWithPruning(self , currentNode , alpha , beta , depth=0):
        moves = ["s" , "d" , "es" , "eo"]

        if(depth > self.maxDepth or (currentNode.player.has_stopped and currentNode.opponent.has_stopped)):
            return self.evaluateFunction(currentNode)


        if(depth % 2 == 0):  # Player: Maximize
            maxTotal = float("-inf")
            for move in moves:
                newNode = self.makeNewNodeByMove(copy.deepcopy(currentNode) , move , "player")
                if(newNode is None):
                    continue

                moveValue = self.minimaxWithPruning(newNode , alpha , beta , depth + 1)
                if(moveValue > beta): # Pruning
                	return moveValue
                
                if(moveValue > maxTotal):
                    maxTotal = moveValue
                    bestMove = move
                    alpha = max(alpha , maxTotal) # Pruning

            if(depth == 0):
                return bestMove
            else:
                return maxTotal

        else:  # Opponent: Minimize
            minTotal = float("inf")
            for move in moves:
                newNode = self.makeNewNodeByMove(copy.deepcopy(currentNode) , move , "opponent")              
                if(newNode is None):
                    continue

                moveValue = self.minimaxWithPruning(newNode , alpha , beta , depth + 1)
                if(moveValue < alpha): # Pruning
                	return moveValue

                if(moveValue < minTotal):
                    minTotal = moveValue
                    beta = min(beta , minTotal) # Pruning

            return minTotal            





playerWins = 0; opponentWins = 0; draws = 0

tic = time.time()
for _ in range(500):
    game = Blacksin(deck_count=21)
    result = game.run()
    if(result == 1):
        playerWins += 1
    elif(result == -1):
        opponentWins += 1
    else:
        draws += 1
toc = time.time()

if(playerWins > opponentWins):
    print("player Wins!")
elif(playerWins < opponentWins):
    print("opponent Wins!")
else:
    print("It's a draw!")

print("Minimax with pruning depth 6 (500 runs)")
print("Number of player wins: " + str(playerWins))
print("Number of opponent wins: " + str(opponentWins))
print("Number of draws: " + str(draws))
print("Time: " + str(toc - tic) + " s")