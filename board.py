from const import *
from square import Square
from piece import *
from move import Move

class Board:
    def __init__(self):
        self.squares = [[0,0,0,0,0,0,0,0]for col in range(COLS)]
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')
        self.last_move = None

    def move(self, piece, move):
        initial = move.initial
        final = move.final

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # move
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def calc_moves(self, piece, row, col):
        '''
            Calculates all possible moves of a specific piece on a specific position 
        '''

        # Define valid piece moves
        def pawn_move():
            if piece.moved:
                steps = 1
            else:
                steps = 2
            # vertical moves
            start = row + piece.dir
            end = row + piece.dir * (1 + steps)
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        #create initial and final move squares
                        initial = Square(row, col)
                        final = Square(move_row, col)
                        #create a move
                        move = Move(initial, final)
                        piece.add_moves(move)
                    # piece is blocked from moving, break
                    else:
                        break
                # move is not in range, break out of if statement
                else:
                    break

            # diagonal moves (take a piece)
            move_row = row + piece.dir
            move_cols = [col-1, col+1]
            for possible_move_col in move_cols:
                if Square.in_range(move_row, possible_move_col):
                    if self.squares[move_row][possible_move_col].has_rival_piece(piece.color):
                        #create initial an fianl move squares
                        initial = Square(row, col)
                        final = Square(move_row, possible_move_col)
                        #create a move
                        move = Move(initial, final)
                        #move that shit
                        piece.add_moves(move)

        def knight_move():
            # 8 possible moves
            possible_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1),
            ]
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        # New Move to be entered
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col) #piece=piece
                        # Move the piece
                        move = Move(initial, final)
                        piece.add_moves(move)

        def straight_lines(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        # create squares of the possible moves
                        initial = Square(row,col)
                        final = Square(possible_move_row, possible_move_col)
                        # create a possible new move
                        move = Move(initial, final)
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            #append a new move
                            piece.add_moves(move)
                        # Has enemy piece?
                        if self.squares[possible_move_row][possible_move_col].has_rival_piece(piece.color):
                            #append a new move
                            piece.add_moves(move)
                            break #exit loop if there is an enemy piece (stop drawing, dumbass!)
                        # Has team piece
                        if self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break #exit the loop if you're running into your own piece (stop drawing, dumbass!)

                    # break if not in range!!
                    else: break

                    # incrementing incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_move():
            adjs = [
                (row-1, col+0), #up
                (row-1, col+1), #up-right
                (row+0, col+1), #right
                (row+1, col+1), #down-right
                (row+1, col+0), #down
                (row+1, col-1), #down-left
                (row+0, col-1), #left
                (row-1, col-1)  #up-left
            ]

            # Normal king moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        #create squares of the new move
                        initial = Square(row,col)
                        final = Square(possible_move_row, possible_move_col) #piece=piece
                        #create new move
                        move = Move(initial, final)
                        #append a new move
                        piece.add_moves(move)
            # Castling rules

            # Queen-side Castling

            # King-side Castling


        # If the instance is a particular piece...
        if isinstance(piece, Pawn):
            pawn_move()
        elif isinstance(piece, Knight):
            knight_move()
        elif isinstance(piece, Bishop):
            straight_lines([
                (-1, 1),    # up-right
                (-1, -1),   # up-left
                (1,1),      # down-right
                (1,-1)      # down-left
            ])
        elif isinstance(piece, Rook):
            straight_lines([
                (-1, 0),    # up
                (0, 1),     # left
                (1, 0),     # down
                (0, -1)     # right
            ])
        elif isinstance(piece, Queen):
            straight_lines([
                (-1, 1),    # up-right
                (-1, -1),   # up-left
                (1, 1),     # down-right
                (1,- 1),    # down-left
                (-1, 0),    # up
                (0, 1),     # left
                (1, 0),     # down
                (0, -1)     # right
            ])
        elif isinstance(piece, King):
            king_move()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # Create all the pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
        
        # Create all the knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # Create all the bishops 
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # Create all the rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # Create the queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # Create the king
        self.squares[row_other][4] = Square(row_other, 4, King(color))

