import sys
import random
import signal
<<<<<<< HEAD
=======
from action import Action
EMPTY = '-'
>>>>>>> 8ba3e4df2c18f9e4d8dcd845032234156ff3b8b5

#Timer handler, helper function

class TimedOutExc(Exception):
    pass

def handler(signum, frame):
    #print 'Signal handler called with signal', signum
    raise TimedOutExc()

<<<<<<< HEAD
=======
class UTTTBoard:
    def __init__(self, boards=list()):
        self._boards = boards
        i = len(boards)
        while i < 9:
            self._boards.append(MiniBoard())
            i += 1
        self._winner = None
        self._available_boards = [i for i in xrange(9) if
                                  self._boards[i].is_board_full() == False]

    def do_move(self, player, miniB_index, inner_index):
        assert (miniB_index in self._available_boards)
        self.get_miniBoard(miniB_index).do_move(player, inner_index)
        self._assess_board()
        if self.get_miniBoard(miniB_index).is_board_full():
            self._available_boards.remove(miniB_index)

    def _assess_board(self):
        if self._winner is not None:
            return
        get_func = lambda obj, index: (self._boards[index].get_winner() or EMPTY)
        self._winner = assess_board(self._boards, get_func)


    def has_winner(self):
        return (self._winner is not None)

    def get_winner(self):
        return self._winner

    def is_board_full(self):
        return len(self._available_boards) == 0

    def get_miniBoard(self, index):
        assert (0 <= index < 9)
        return self._boards[index]

    def get_single_cell(self, miniBoard_pos, inner_pos):
        return self.get_miniBoard(miniBoard_pos).get(inner_pos)

    def deep_copy(self):
        dup_boards = [miniB.deep_copy() for miniB in self._boards]
        dup = UTTTBoard(dup_boards)
        dup._winner = self._winner
        return dup

    def convert_t2D(self):
        full_board = []
        for miniB_row in xrange(3):
            for inner_row in xrange(3):
                row = []
                for col in xrange(3):
                    mini = (self._boards)[miniB_row * 3 + col]
                    middle = str(mini.get_winner()) if inner_row == 1 else SPACE
                    row.extend(mini.get_board()[
                               inner_row * 3: inner_row * 3 + 3] if not mini.has_winner() else [
                        SPACE, middle, SPACE])
                full_board.append(row)
        return full_board

    def convert_tMiniB(self):
        return MiniBoard([(innerB.get_winner() or EMPTY) for innerB in self._boards])

    def __str__(self):
        return '\n'.join([str(miniB) for miniB in self._boards])

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class State:
    def __init__(self, uttt=None, player=Player(), mini_board=None):
        self._uttt = UTTTBoard() if uttt is None else uttt.deep_copy()
        self.player_turn = player  # default to x's turn
        self.mini_board = mini_board
        self._last_move = None

    def get_legal_actions(self):
        acts = []
        miniBs = [self.mini_board] if self.mini_board is not None else range(9)
        #debug('available miniBs: %s' % miniBs)
        for board_index in miniBs:
            legal_cells = self._uttt.get_miniBoard(board_index).get_legal_cells()
            for cell in legal_cells:
                acts.append(Action(board_index, cell))
        return acts

    def generate_successor(self, act):
        new_state = State(self._uttt, self.player_turn.opponent(), act.inner_index)
        new_state._uttt.do_move(self.player_turn, act.miniB_index, act.inner_index)
        new_state._last_move = act
        if new_state._uttt.get_miniBoard(act.inner_index).is_board_full():
            new_state.mini_board = None
        return new_state

    def is_terminal(self):
        return self._uttt.has_winner() or self._uttt.is_board_full()

    def get_last_move(self):
        return self._last_move

    def get_board(self):
        return self._uttt

    def get_player(self):
        return self.player_turn

    '''def draw(self):
        if Game.ENABLE_GRAPHICS:
            print 'Player %s turn: (board state befor the move)' % self.player_turn
            draw_board(self._uttt, self.mini_board)
    '''

    def deep_copy(self):
        new_state = State(self._uttt, self.player_turn, self.mini_board)
        new_state._last_move = self._last_move
        return new_state

    def __str__(self):
        return str(self._uttt) + str(self.player_turn)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class WinningPossibilitiesHeu(Heuristic):
    #parameters for that heuristics
    APPROXIMATE_WIN_SCORE = 7
    BIG_BOARD_WEIGHT = 23
    WIN_SCORE = 10**6
    POSSIBLE_WIN_SEQUENCES = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]

    def get_evaluate_function(player_obj):
        return lambda some_state: WinningPossibilitiesHeu.__eval_state(some_state, player_obj)

    def __eval_state(state, player):
        uttt_board = state.get_board()
        if uttt_board.has_winner():
            winner = uttt_board.get_winner()
            free_cells = 0
            for i in xrange(9):
                miniB = uttt_board.get_miniBoard(i)
                free_cells += len(miniB.get_legal_cells())
            return WinningPossibilitiesHeu.WIN_SCORE + free_cells if winner == str(player) else -WinningPossibilitiesHeu.WIN_SCORE - free_cells
        if uttt_board.is_board_full():
            return 0
        board_as_mini = uttt_board.convert_tMiniB()
        ret = WinningPossibilitiesHeu.__assess_miniB(board_as_mini, player) * WinningPossibilitiesHeu.BIG_BOARD_WEIGHT
        for i in xrange(9):
            miniB = uttt_board.get_miniBoard(i)
            if not miniB.is_board_full():
                ret += WinningPossibilitiesHeu.__assess_miniB(miniB, player)
        return ret

    def __assess_miniB(miniB, player):
        if miniB.is_board_full():
            return 0
        player_counter = 0
        opponent_counter = 0
        player_str = str(player)
        opponent_str = str(player.opponent())
        miniB_as_list = miniB.get_board()
        for seq in WinningPossibilitiesHeu.POSSIBLE_WIN_SEQUENCES:
            filtered_seq = [miniB_as_list[index] for index in seq if miniB_as_list[index] != EMPTY]
            if player_str in filtered_seq:
                if opponent_str in filtered_seq:
                    continue
                if len(filtered_seq) > 1:
                    player_counter += WinningPossibilitiesHeu.APPROXIMATE_WIN_SCORE
                player_counter += 1
            elif opponent_str in filtered_seq:
                if len(filtered_seq) > 1:
                    opponent_counter += WinningPossibilitiesHeu.APPROXIMATE_WIN_SCORE
                opponent_counter += 1
        return player_counter - opponent_counter


class AlphaBetha:
    # The searching depth of the alpha-beta. Note that the depth decrease only on opponents turns
    # therefor the actual depth in the game tree is TWICE the value of ALPHA_BETA_DEPTH.
    ALPHA_BETA_DEPTH = 2

    def __runAB(eval_func, state):
        acts_res = []
        for act in state.get_legal_actions():
            successor_state = state.generate_successor(act)
            acts_res.append((act, AlphaBetha.__min_val_ab(eval_func, successor_state, AlphaBetha.ALPHA_BETA_DEPTH)))
        _, best_val = max(acts_res, key=lambda x: x[1])
        return random.choice([best_action for best_action, val in acts_res if val == best_val])
    
    def __min_val_ab(eval_func, state, depth, alpha=-sys.maxint, beta=sys.maxint):
        if AlphaBetha.__terminal_test(state, depth):
            return eval_func(state)
        val = sys.maxint
        for act in state.get_legal_actions():
            successor_state = state.generate_successor(act)
            val = min(val, AlphaBetha.__max_val_ab(eval_func, successor_state, depth - 1, alpha, beta))
            if val <= alpha:
                return val
            beta = min(beta, val)
        return val
    
    def __max_val_ab(eval_func, state, depth, alpha=-sys.maxint, beta=sys.maxint):
        if AlphaBetha.__terminal_test(state, depth):
            return eval_func(state)
        val = -sys.maxint
        for act in state.get_legal_actions():
            successor_state = state.generate_successor(act)
            val = max(val, AlphaBetha.__min_val_ab(eval_func, successor_state, depth, alpha, beta))
            if val >= beta:
                return val
            alpha = max(alpha, val)
        return val
    
    def __terminal_test(state, depth):
        return state.is_terminal() or (depth == 0)

    def __init__(self, heuristic, player_obj):
        self._eval_func = heuristic.get_evaluate_function(player_obj)

    def choose_act(self, state):
        return AlphaBetha.__runAB(self._eval_func, state)

>>>>>>> 8ba3e4df2c18f9e4d8dcd845032234156ff3b8b5

class Manual_player:
	def __init__(self):
		pass
	def move(self, temp_board, temp_block, old_move, flag):
		print 'Enter your move: <format:row column> (you\'re playing with', flag + ")"	
		mvp = raw_input()
		mvp = mvp.split()
		return (int(mvp[0]), int(mvp[1]))
		

class Player1:
	
	def __init__(self):
		pass

	def move(self, temp_board, temp_block, old_move, flag):
		#while(1):
			#pass
		for_corner = [0,2,3,5,6,8]

		#List of permitted blocks, based on old move.
		blocks_allowed  = []

		if old_move[0] in for_corner and old_move[1] in for_corner:
			## we will have 3 representative blocks, to choose from

			if old_move[0] % 3 == 0 and old_move[1] % 3 == 0:
				## top left 3 blocks are allowed
				blocks_allowed = [0, 1, 3]
			elif old_move[0] % 3 == 0 and old_move[1] in [2, 5, 8]:
				## top right 3 blocks are allowed
				blocks_allowed = [1,2,5]
			elif old_move[0] in [2,5, 8] and old_move[1] % 3 == 0:
				## bottom left 3 blocks are allowed
				blocks_allowed  = [3,6,7]
			elif old_move[0] in [2,5,8] and old_move[1] in [2,5,8]:
				### bottom right 3 blocks are allowed
				blocks_allowed = [5,7,8]
			else:
				print "SOMETHING REALLY WEIRD HAPPENED!"
				sys.exit(1)
		else:
		#### we will have only 1 block to choose from (or maybe NONE of them, which calls for a free move)
			if old_move[0] % 3 == 0 and old_move[1] in [1,4,7]:
				## upper-center block
				blocks_allowed = [1]
	
			elif old_move[0] in [1,4,7] and old_move[1] % 3 == 0:
				## middle-left block
				blocks_allowed = [3]
		
			elif old_move[0] in [2,5,8] and old_move[1] in [1,4,7]:
				## lower-center block
				blocks_allowed = [7]

			elif old_move[0] in [1,4,7] and old_move[1] in [2,5,8]:
				## middle-right block
				blocks_allowed = [5]
			elif old_move[0] in [1,4,7] and old_move[1] in [1,4,7]:
				blocks_allowed = [4]

	# We get all the empty cells in allowed blocks. If they're all full, we get all the empty cells in the entire board.
		cells = get_empty_out_of(temp_board, blocks_allowed)
		return cells[random.randrange(len(cells))]

class Player2:
	
	def __init__(self):
		pass
	def move(self,temp_board,temp_block,old_move,flag):
		for_corner = [0,2,3,5,6,8]

		#List of permitted blocks, based on old move.
		blocks_allowed  = []

		if old_move[0] in for_corner and old_move[1] in for_corner:
			## we will have 3 representative blocks, to choose from

			if old_move[0] % 3 == 0 and old_move[1] % 3 == 0:
				## top left 3 blocks are allowed
				blocks_allowed = [0, 1, 3]
			elif old_move[0] % 3 == 0 and old_move[1] in [2, 5, 8]:
				## top right 3 blocks are allowed
				blocks_allowed = [1,2,5]
			elif old_move[0] in [2,5, 8] and old_move[1] % 3 == 0:
				## bottom left 3 blocks are allowed
				blocks_allowed  = [3,6,7]
			elif old_move[0] in [2,5,8] and old_move[1] in [2,5,8]:
				### bottom right 3 blocks are allowed
				blocks_allowed = [5,7,8]
			else:
				print "SOMETHING REALLY WEIRD HAPPENED!"
				sys.exit(1)
		else:
		#### we will have only 1 block to choose from (or maybe NONE of them, which calls for a free move)
			if old_move[0] % 3 == 0 and old_move[1] in [1,4,7]:
				## upper-center block
				blocks_allowed = [1]
	
			elif old_move[0] in [1,4,7] and old_move[1] % 3 == 0:
				## middle-left block
				blocks_allowed = [3]
		
			elif old_move[0] in [2,5,8] and old_move[1] in [1,4,7]:
				## lower-center block
				blocks_allowed = [7]

			elif old_move[0] in [1,4,7] and old_move[1] in [2,5,8]:
				## middle-right block
				blocks_allowed = [5]
			elif old_move[0] in [1,4,7] and old_move[1] in [1,4,7]:
				blocks_allowed = [4]

	# We get all the empty cells in allowed blocks. If they're all full, we get all the empty cells in the entire board.
		cells = get_empty_out_of(temp_board,blocks_allowed)
		return cells[random.randrange(len(cells))]

#Initializes the game
def get_init_board_and_blockstatus():
	board = []
	for i in range(9):
		row = ['-']*9
		board.append(row)
	
	block_stat = ['-']*9
	return board, block_stat

# Checks if player has messed with the board. Don't mess with the board that is passed to your move function. 
def verification_fails_board(board_game, temp_board_state):
	return board_game == temp_board_state	

# Checks if player has messed with the block. Don't mess with the block array that is passed to your move function. 
def verification_fails_block(block_stat, temp_block_stat):
	return block_stat == temp_block_stat	

#Gets empty cells from the list of possible blocks. Hence gets valid moves. 
def get_empty_out_of(gameb, blal):
	cells = []  # it will be list of tuples
	#Iterate over possible blocks and get empty cells
	for idb in blal:
		id1 = idb/3
		id2 = idb%3
		for i in range(id1*3,id1*3+3):
			for j in range(id2*3,id2*3+3):
				if gameb[i][j] == '-':
					cells.append((i,j))

	# If all the possible blocks are full, you can move anywhere
	if cells == []:
		for i in range(9):
			for j in range(9):
				if gameb[i][j] == '-':
					cells.append((i,j))	
		
	return cells
		
# Note that even if someone has won a block, it is not abandoned. But then, there's no point winning it again!
# Returns True if move is valid
def check_valid_move(game_board, current_move, old_move):

	# first we need to check whether current_move is tuple of not
	# old_move is guaranteed to be correct
	if type(current_move) is not tuple:
		return False
	
	if len(current_move) != 2:
		return False

	a = current_move[0]
	b = current_move[1]	

	if type(a) is not int or type(b) is not int:
		return False
	if a < 0 or a > 8 or b < 0 or b > 8:
		return False

	#Special case at start of game, any move is okay!
	if old_move[0] == -1 and old_move[1] == -1:
		return True


	for_corner = [0,2,3,5,6,8]

	#List of permitted blocks, based on old move.
	blocks_allowed  = []

	if old_move[0] in for_corner and old_move[1] in for_corner:
		## we will have 3 representative blocks, to choose from

		if old_move[0] % 3 == 0 and old_move[1] % 3 == 0:
			## top left 3 blocks are allowed
			blocks_allowed = [0, 1, 3]
		elif old_move[0] % 3 == 0 and old_move[1] in [2, 5, 8]:
			## top right 3 blocks are allowed
			blocks_allowed = [1,2,5]
		elif old_move[0] in [2,5, 8] and old_move[1] % 3 == 0:
			## bottom left 3 blocks are allowed
			blocks_allowed  = [3,6,7]
		elif old_move[0] in [2,5,8] and old_move[1] in [2,5,8]:
			### bottom right 3 blocks are allowed
			blocks_allowed = [5,7,8]

		else:
			print "SOMETHING REALLY WEIRD HAPPENED!"
			sys.exit(1)

	else:
		#### we will have only 1 block to choose from (or maybe NONE of them, which calls for a free move)
		if old_move[0] % 3 == 0 and old_move[1] in [1,4,7]:
			## upper-center block
			blocks_allowed = [1]
	
		elif old_move[0] in [1,4,7] and old_move[1] % 3 == 0:
			## middle-left block
			blocks_allowed = [3]
		
		elif old_move[0] in [2,5,8] and old_move[1] in [1,4,7]:
			## lower-center block
			blocks_allowed = [7]

		elif old_move[0] in [1,4,7] and old_move[1] in [2,5,8]:
			## middle-right block
			blocks_allowed = [5]

		elif old_move[0] in [1,4,7] and old_move[1] in [1,4,7]:
			blocks_allowed = [4]


	# We get all the empty cells in allowed blocks. If they're all full, we get all the empty cells in the entire board.
	cells = get_empty_out_of(game_board, blocks_allowed)

	#Checks if you made a valid move. 
	if current_move in cells:
		return True
	else:
		return False

def update_lists(game_board, block_stat, move_ret, fl):
	#move_ret has the move to be made, so we modify the game_board, and then check if we need to modify block_stat
	game_board[move_ret[0]][move_ret[1]] = fl


	#print "@@@@@@@@@@@@@@@@@"
	#print block_stat

	block_no = (move_ret[0]/3)*3 + move_ret[1]/3	
	id1 = block_no/3
	id2 = block_no%3
	mg = 0
	mflg = 0
	if block_stat[block_no] == '-':

		### now for diagonals
		## D1
		# ^
		#   ^
		#     ^
		if game_board[id1*3][id2*3] == game_board[id1*3+1][id2*3+1] and game_board[id1*3+1][id2*3+1] == game_board[id1*3+2][id2*3+2] and game_board[id1*3+1][id2*3+1] != '-':
			mflg=1
			mg=1
			#print "SEG: D1 found"

		## D2
		#     ^
		#   ^
		# ^
		############ MODIFICATION HERE, in second condition -> gb[id1*3][id2*3+2]
		# if game_board[id1*3+2][id2*3] == game_board[id1*3+1][id2*3+1] and game_board[id1*3+1][id2*3+1] == game_board[id1*3+2][id2*3] and game_board[id1*3+1][id2*3+1] != '-':
		if game_board[id1*3+2][id2*3] == game_board[id1*3+1][id2*3+1] and game_board[id1*3+1][id2*3+1] == game_board[id1*3][id2*3 + 2] and game_board[id1*3+1][id2*3+1] != '-':
			mflg=1
			mg=1
			#print "SEG: D2 found"

		### col-wise
		if mflg != 1:
                    for i in range(id2*3,id2*3+3):
                        #### MODIFICATION HERE, [i] was missing previously
                        # if game_board[id1*3]==game_board[id1*3+1] and game_board[id1*3+1] == game_board[id1*3+2] and game_board[id1*3] != '-':
                        if game_board[id1*3][i]==game_board[id1*3+1][i] and game_board[id1*3+1][i] == game_board[id1*3+2][i] and game_board[id1*3][i] != '-':
                                mflg = 1
				#print "SEG: Col found"
                                break

                ### row-wise
		if mflg != 1:
                    for i in range(id1*3,id1*3+3):
                        ### MODIFICATION HERE, [i] was missing previously
                        #if game_board[id2*3]==game_board[id2*3+1] and game_board[id2*3+1] == game_board[id2*3+2] and game_board[id2*3] != '-':
                        if game_board[i][id2*3]==game_board[i][id2*3+1] and game_board[i][id2*3+1] == game_board[i][id2*3+2] and game_board[i][id2*3] != '-':
                                mflg = 1
				#print "SEG: Row found"
                                break

	
	if mflg == 1:
		block_stat[block_no] = fl

	#print 
	#print block_stat
	#print "@@@@@@@@@@@@@@@@@@@@@@@"	
	return mg

#Check win
def terminal_state_reached(game_board, block_stat,point1,point2):
	### we are now concerned only with block_stat
	bs = block_stat
	## Row win
	if (bs[0] == bs[1] and bs[1] == bs[2] and bs[1]!='-') or (bs[3]!='-' and bs[3] == bs[4] and bs[4] == bs[5]) or (bs[6]!='-' and bs[6] == bs[7] and bs[7] == bs[8]):
		print block_stat
		return True, 'W'
	## Col win
	elif (bs[0] == bs[3] and bs[3] == bs[6] and bs[0]!='-') or (bs[1] == bs[4] and bs[4] == bs[7] and bs[4]!='-') or (bs[2] == bs[5] and bs[5] == bs[8] and bs[5]!='-'):
		print block_stat
		return True, 'W'
	## Diag win
	elif (bs[0] == bs[4] and bs[4] == bs[8] and bs[0]!='-') or (bs[2] == bs[4] and bs[4] == bs[6] and bs[2]!='-'):
		print block_stat
		return True, 'W'
	else:
		smfl = 0
		for i in range(9):
			for j in range(9):
				if game_board[i][j] == '-':
					smfl = 1
					break
		if smfl == 1:
			return False, 'Continue'
		
		else:
			##### check of number of DIAGONALs


			if point1>point2:
				return True, 'P1'
			elif point2>point1:
				return True, 'P2'
			else:
				return True, 'D'	


def decide_winner_and_get_message(player,status, message):
	if status == 'P1':
		return ('P1', 'MORE DIAGONALS')
	elif status == 'P2':
		return ('P2', 'MORE DIAGONALS')
	elif player == 'P1' and status == 'L':
		return ('P2',message)
	elif player == 'P1' and status == 'W':
		return ('P1',message)
	elif player == 'P2' and status == 'L':
		return ('P1',message)
	elif player == 'P2' and status == 'W':
		return ('P2',message)
	else:
		return ('NONE','DRAW')
	return


def print_lists(gb, bs):
	print '=========== Game Board ==========='
	for i in range(9):
		if i > 0 and i % 3 == 0:
			print
		for j in range(9):
			if j > 0 and j % 3 == 0:
				print " " + gb[i][j],
			else:
				print gb[i][j],

		print
	print "=================================="

	print "=========== Block Status ========="
	for i in range(0, 9, 3):
		print bs[i] + " " + bs[i+1] + " " + bs[i+2] 
	print "=================================="
	print
	

def simulate(obj1,obj2):
	
	# game board is a 9x9 list, block_stat is a 1D list of 9 elements
	game_board, block_stat = get_init_board_and_blockstatus()

	#########
	# deciding player1 / player2 after a coin toss
	pl1 = obj1 
	pl2 = obj2

	### basically, player with flag 'x' will start the game
	pl1_fl = 'x'
	pl2_fl = 'o'

	old_move = (-1, -1) ### for the first move

	WINNER = ''
	MESSAGE = ''
	TIMEALLOWED = 60


	### These points will not keep track of the total points of both the players.
	### Instead, these variables will keep track of only the blocks won by DIAGONALS, and these points will be used only in cases of DRAW....
	p1_pts=0
	p2_pts=0

	#### printing
	print_lists(game_board, block_stat)

	while(1):
		###################################### 
		########### firstly pl1 will move
		###################################### 
		
		## just for checking that the player1 does not modify the contents of the 2 lists
		temp_board_state = game_board[:]
		temp_block_stat = block_stat[:]
	
		signal.signal(signal.SIGALRM, handler)
		signal.alarm(TIMEALLOWED)
		# Player1 to complete in TIMEALLOWED secs. 
		try:
			ret_move_pl1 = pl1.move(temp_board_state, temp_block_stat, old_move, pl1_fl)
		except TimedOutExc as e:
			WINNER, MESSAGE = decide_winner_and_get_message('P1', 'L',   'TIMED OUT')
			break
			### MODIFICATION!!
		signal.alarm(0)
	
		#### check if both lists are the same!!
		if not (verification_fails_board(game_board, temp_board_state) and verification_fails_block(block_stat, temp_block_stat)):
			##player1 loses - he modified something
			WINNER, MESSAGE = decide_winner_and_get_message('P1', 'L',   'MODIFIED CONTENTS OF LISTS')
			break
		
		### now check if the returned move is valid
		if not check_valid_move(game_board, ret_move_pl1, old_move):
			## player1 loses - he made the wrong move.
			WINNER, MESSAGE = decide_winner_and_get_message('P1', 'L',   'MADE AN INVALID MOVE')
			break
			

		print "Player 1 made the move:", ret_move_pl1, 'with', pl1_fl
		######## So if the move is valid, we update the 'game_board' and 'block_stat' lists with move of pl1
		p1_pts += update_lists(game_board, block_stat, ret_move_pl1, pl1_fl)

		### now check if the last move resulted in a terminal state
		gamestatus, mesg =  terminal_state_reached(game_board, block_stat,p1_pts,p2_pts)
		if gamestatus == True:
			print_lists(game_board, block_stat)
			WINNER, MESSAGE = decide_winner_and_get_message('P1', mesg,  'COMPLETE')	
			break

		
		old_move = ret_move_pl1
		print_lists(game_board, block_stat)
		############################################
		### Now player2 plays
		###########################################
		
                ## just for checking that the player2 does not modify the contents of the 2 lists
                temp_board_state = game_board[:]
                temp_block_stat = block_stat[:]


		signal.signal(signal.SIGALRM, handler)
		signal.alarm(TIMEALLOWED)
		# Player2 to complete in TIMEALLOWED secs. 
		try:
                	ret_move_pl2 = pl2.move(temp_board_state, temp_block_stat, old_move, pl2_fl)
		except TimedOutExc as e:
			WINNER, MESSAGE = decide_winner_and_get_message('P2', 'L',   'TIMED OUT')
			break
		signal.alarm(0)

                #### check if both lists are the same!!
                if not (verification_fails_board(game_board, temp_board_state) and verification_fails_block(block_stat, temp_block_stat)):
                        ##player2 loses - he modified something
			WINNER, MESSAGE = decide_winner_and_get_message('P2', 'L',   'MODIFIED CONTENTS OF LISTS')
			break
			

                ### now check if the returned move is valid
                if not check_valid_move(game_board, ret_move_pl2, old_move):
                        ## player2 loses - he made the wrong move...
			WINNER, MESSAGE = decide_winner_and_get_message('P2', 'L',   'MADE AN INVALID MOVE')
			break


		print "Player 2 made the move:", ret_move_pl2, 'with', pl2_fl
                ######## So if the move is valid, we update the 'game_board' and 'block_stat' lists with the move of P2
                p2_pts += update_lists(game_board, block_stat, ret_move_pl2, pl2_fl)

                ### now check if the last move resulted in a terminal state
		gamestatus, mesg =  terminal_state_reached(game_board, block_stat,p1_pts,p2_pts)
                if gamestatus == True:
			print_lists(game_board, block_stat)
                        WINNER, MESSAGE = decide_winner_and_get_message('P2', mesg,  'COMPLETE' )
                        break
		### otherwise CONTINUE	
		old_move = ret_move_pl2
		print_lists(game_board, block_stat)

	######### THESE ARE NOT THE TOTAL points, these are just the diagonal points, (refer to the part before the while(1) loop
	####### These will be used only in cases of DRAW
	print p1_pts
	print p2_pts

	
	print WINNER
	print MESSAGE
#	return WINNER, MESSAGE, p1_pt2, p2_pt2

if __name__ == '__main__':
	## get game playing objects

	if len(sys.argv) != 2:
		print 'Usage: python simulator.py <option>'
		print '<option> can be 1 => Random player vs. Random player'
		print '                2 => Human vs. Random Player'
		print '                3 => Human vs. Human'
		sys.exit(1)
 
	obj1 = ''
	obj2 = ''
	option = sys.argv[1]	
	if option == '1':
		obj1 = Player1()
		obj2 = Player2()

	elif option == '2':
		obj1 = Player1()
		obj2 = Manual_player()
	elif option == '3':
		obj1 = Manual_player()
		obj2 = Manual_player()


        #########
        # deciding player1 / player2 after a coin toss
        num = random.uniform(0,1)
	interchange = 0
        if num > 0.5:
		interchange = 1
		simulate(obj2, obj1)
	else:
		simulate(obj1, obj2)
		
	
