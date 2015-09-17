#! /usr/bin/env python

from copy import copy
from numpy import array
import platform
import os

#-----Create the Board----------------------------------------------------

board=array([array([None]*8)]*8)                                     # Create an 8x8 matrix as the board

#-----Set Global Variables------------------------------------------------

homerow={ 'w' : 7 , 'b' : 0 }                                        # The starting row of each colour's king

winner=None                                                          # Nobody starts off as a winner!

cols_ids=['a','b','c','d','e','f','g','h']                           # Valid column labels

b_directions=[(1,1),(1,-1),(-1,1),(-1,-1)]                              # Diagonal Directions (1-space bishop-like moves)
r_directions=[(1,0),(0,1),(-1,0),(0,-1)]                                # Diagonal Directions (1-space bishop-like moves)
n_directions=[(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]  # Knight-like moves
p_directions={ 'w' : -1 , 'b' : 1 }                                     # The direction pawns must move for each player

system=platform.system().lower()                                     # Fetch operating system for the sake of system commands

#-----Basic Function Definitions------------------------------------------

def on_board(col,row):                                               # Checks whether the coordinates fed to it correspond to a square on the board
   if col>7: return False
   if row>7: return False
   if col<0: return False
   if row<0: return False
   return True

def square_to_cell(square):                                          # Convert user input to grid location
   assert len(square)==2
   try:
      int(square[1])                                                 # See if the second character is a number.  If not, effectively flip input
      col,row=square[0],square[1]
   except:
      row,col=square[0],square[1]
   col=col.lower()
   row=int(row)-1                                                    # Convert human-readable row into machine-readable row

   if col=='a':   col=0                                              # Convert letter into column
   elif col=='b': col=1
   elif col=='c': col=2
   elif col=='d': col=3
   elif col=='e': col=4
   elif col=='f': col=5
   elif col=='g': col=6
   elif col=='h': col=7
   else: col=8                                                       # Pass this token as a failure if it couldnt resolve the column

   assert on_board(col,row)

   return col,row

def clear():                                                         # Passes correct clear command to the system       
   if system=='windows':
      os.system('cls')
   else:
      os.system('clear')

def piece_to_text(pID):                                              # Take piece ID and return its name in human language
   if pID=='k': return 'King'
   elif pID=='q': return 'Queen'
   elif pID=='r': return 'Rook'
   elif pID=='b': return 'Bishop'
   elif pID=='n': return 'Knight'
   elif pID=='p': return 'Pawn'
   else: return 'None'

def col_to_text(cID):                                                # Take colour ID and return its name in human language
   if cID=='w': return 'White'
   elif cID=='b': return 'Black'
   else: return 'None'

def not_(player):                                                    # Return the player that wasnt input
   if player=='w': return 'b'
   else: return 'w'

#-----Check Checkers------------------------------------------------------

def cell_in_check(colour,cell):                                      # Check if an arbitrary cell (as a tuple) is threatened by the opponent

   danger_squares=set([])
   for ID in pieces:                                                 # For all pieces
      if (not pieces[ID].taken) and (pieces[ID].colour != colour):   # Collect all threatened squares
         danger_squares=danger_squares | pieces[ID].get_legal()      # Add new entries to set of threatened squares

   ##########             # Uncomment this for diagnostics; shows a grid of 'danger_squares' each time cell_in_check is called

   #for j in range(8):
   #   print '   +---+---+---+---+---+---+---+---+'
   #   rstr=' '+str(j+1)+' |'
   #   for i in range(8):
   #      if (i,j) in danger_squares:
   #         rstr+=' x '
   #      else:
   #         rstr+='   '
   #      rstr+='|'
   #   print rstr
   #print '   +---+---+---+---+---+---+---+---+'
   #raw_input('')

   ##########

   return cell in danger_squares                                     # Return whether cell in question is threatened

def check_check(colour):                                             # Check if 'colour' player is in check

   king_loc=pieces[colour+'_k'].col,pieces[colour+'_k'].row
   return cell_in_check(colour,king_loc)

def into_check(colour,f_col,f_row,t_col,t_row):                      # Check if a move would place the active player into check by virtually performing that move

   # SAVE_ID_FROM and SAVE_ID_TO

   save_id_f=board[f_col][f_row]                                     # Save the identity of the piece in the starting cell
   save_id_t=board[t_col][t_row]                                     # Save the identity of the piece in the ending cell

   en_passant=False
   if pieces[save_id_f].type=='p' and save_id_t==None and t_col!=f_col:
      en_passant=True                                                # Flag if the move is an en-passant move
      save_id_e=board[t_col][f_row]                                  # Save position of piece ro be taken en passant
      pieces[save_id_e].row=None                                     # Force "Take" of en passant victim
      pieces[save_id_e].col=None
      pieces[save_id_e].taken=True
   elif save_id_t!=None:                                             # Else, if not 'en passant'
      pieces[save_id_t].row=None                                     # Force "Take" of victim
      pieces[save_id_t].col=None
      pieces[save_id_t].taken=True

   pieces[save_id_f].row=t_row                                       # Move active piece without changing its 'last moved' parameter
   pieces[save_id_f].col=t_col
   board[f_col][f_row]=None
   board[t_col][t_row]=save_id_f

   is_in_check=check_check(colour)                                   # Return whether 'colour' player is now in check

   pieces[save_id_f].row=f_row                                       # Restore internal row and column of active piece
   pieces[save_id_f].col=f_col

   if en_passant:
      pieces[save_id_e].row=f_row                                    # Restore internal row and column of en passant victim
      pieces[save_id_e].col=t_col
      pieces[save_id_e].taken=True
   elif save_id_t!=None:
      pieces[save_id_t].row=t_row                                    # Restore internal row and column of standard take victim
      pieces[save_id_t].col=t_col
      pieces[save_id_t].taken=False

   board[f_col][f_row]=save_id_f                                     # Reset the board
   board[t_col][t_row]=save_id_t
   if en_passant:
      board[t_col][f_row]=save_id_e

   return is_in_check

def can_move(colour):                                                # Check if any legal moves are available to a player
   is_legal_move=False

   for ID in pieces:                                                 # For every piece
      if (pieces[ID].colour!=colour) or (pieces[ID].taken):          # Abort if piece is taken or belongs to enemy
         continue
      legal_s_c=pieces[ID].col                                       # Save location of piece
      legal_s_r=pieces[ID].row
      moves=pieces[ID].get_legal()                                   # Get all possible moves of piece
      for move in moves:                                             # Check if each possible move would place player into check
         legal_e_c=move[0]
         legal_e_r=move[1]
         is_legal_move=not into_check(colour,legal_s_c,legal_s_r,legal_e_c,legal_e_r)
         if is_legal_move:                                           # If ANY legal moves are found ever, immediately return true
            return True

   return False                                                      # If no legal moves are found, return False

#-----Define Piece Superclass---------------------------------------------

class piece:                                                         # Functions common to all piece types
   def __init__(self,col,row,colour,ID):                             # Piece setup:
      self.col,self.row=col,row                                      # Save internal row and column
      self.taken=False                                               # No piece starts off taken
      self.ID=ID                                                     # Save internal ID string
      self.typ_val()                                                 # Fetch type and value of piece
      self.colour=colour                                             # Save internal colour string
      self.moves=0                                                   # Save number of times the piece has moved (used for en passant)
      self.last_moved=turn                                           # Save the last time the piece moved (used for en passant, castling)
      board[self.col][self.row]=ID                                   # Write this piece's ID on the correct cell in the board array

   def typ_val(self):                                                # Return null type and value if not otherwise given
      self.value=0
      self.type=None

   def get_legal(self):                                              # Return null set of legal moves if no function to find them is given
      return set([])

   def move(self,square):                                            # Define how to move a piece

      to_col,to_row=square_to_cell(square)                           # Fetch cell

      board[self.col][self.row]=None                                 # Blank the cell that formerly contained the piece

      self.col=to_col                                                # Overwrite internal row and column values
      self.row=to_row

      if board[self.col][self.row]!=None:                            # Take a piece if its on the square you're trying to move to
         pieces[board[self.col][self.row]].take()

      board[self.col][self.row]=self.ID                              # Update board with new location of this piece
      self.last_moved=turn                                           # Update the last time this piece was moved
      self.moves+=1                                                  # Update the number of moves this piece has taken

   def take(self):                                                   # What to do if this piece is taken
      self.taken=True                                                # Set internal taken status to true
      self.col=None                                                  # Blank internal row and column
      self.row=None
      score[not_(self.colour)]+=self.value                           # Add this piece's value to the opponent's score
      global taken_this_turn
      taken_this_turn=self.type                                      # Broadcast the taken piece's type                    

   def try_move(self,square):                                        # Check if a move is allowed and, if so, do it.
      trycol,tryrow=square_to_cell(square)
      if (trycol,tryrow) in self.get_legal():                        # Check if attempted move is in the legal set for this piece
         self.move(square)                                           # If it is, do it
         return True
      else:
         return False

#-----Define legal squares function for straight-line moves---------------

def get_legal_lin(directions,colour,row,col,maxstep=7):
      lin_legal=[]
      for test in directions:                                        # For each direction:
         steps=1                                                     # Set distance to one
         while True:
            if steps>maxstep: break                                  # If step size is greater than the maximum (default 7), abort
            t_col=col+test[0]*steps                                  # Attempt to go [distance] squares in [direction]
            t_row=row+test[1]*steps
            if not on_board(t_col,t_row): break                      # If the square is off the board, move onto the next direction
            if board[t_col][t_row]!=None:
               if pieces[board[t_col][t_row]].colour==colour:        # If square is occupied by friendly piece, move onto the next direction
                  break
               else:
                  lin_legal.append((t_col,t_row))                    # If square is occupied by enemy piece, add to legal set and move onto the next direction
                  break
            else:
               lin_legal.append((t_col,t_row))                       # If there is nothing in the square, add to legal set and increase distance
               steps+=1

      return lin_legal

#-----Define Pieces-------------------------------------------------------

#---PAWN------------------------------------------

class pawn(piece):                                                   # Define the pawn
   def typ_val(self):
      self.type='p'
      self.value=1                                                   # Pawn's value is 1

   def get_legal(self):                                              # Define legal move set for a pawn:
      legal=[]

      p_dir=p_directions[self.colour]                                # Obtain the direction (up or down) the pawn should advance

      #-----Normal move (1 forwards)---------

      t_col=self.col                                                 # Fetch row and column of square 1 in front of pawn
      t_row=self.row+p_dir

      for i in range(1):
         if not on_board(t_col,t_row): break                         # If move would take piece off the board, abort
         if board[t_col][t_row]!=None: break                         # If move takes pawn into occupied square, abort
         legal.append((t_col,t_row))                                 # Add 1 forwards to legal move set

      #-----Double-Square Start Move---------

         if self.last_moved==0:                                      # If pawn has not previously moved and normal move is legal
            t_row+=p_dir                                             # Fetch row f square 2 in front of pawn
            if board[t_col][t_row]==None:                            # If move takes pawn into unoccupied square, add 2 forwards to legal move set
               legal.append((t_col,t_row))

      #-----Taking Normally------------------

      for shift in set([1,-1]):                                      # Define an array corresponding to column shifts of +1 and -1
         t_col=self.col+shift                                        # Fetch column and row of each 1-square diagonal in front of the pawn
         t_row=self.row+p_dir

         if not on_board(t_col,t_row): continue                      # Abort if the square is off the board

         if board[t_col][t_row]!=None:                               # If there is a piece in the diagonal
            if pieces[board[t_col][t_row]].colour!=self.colour:      # If the piece does not belong to this pawn's player
               legal.append((t_col,t_row))                           # Add to legal set

      #-----Taking en passant----------------

      for shift in set([1,-1]):
         t_col=self.col+shift
         t_row=self.row+p_dir

         if t_row!=homerow[not_(self.colour)]-(2*p_dir): continue    # Pawn-en-Passant can only ever occur two rows back from enemy's homerow
         if t_col>7: continue
         if t_col<0: continue

         if board[t_col][t_row]!=None: continue                      # If something blocks end of move, abort
         if board[t_col][self.row]==None: continue                   # If nothing to take en passant, abort
         ep_ID=board[t_col][self.row]                                # Store en passant victim's ID for some brutal interrogation
         if pieces[ep_ID].colour==self.colour: continue              # If you're trying to en passant your own piece, abort
         if pieces[ep_ID].type!='p': continue                        # If you're trying to en passant something which isnt a pawn, abort
         if pieces[ep_ID].moves!=1:  continue                        # If the victim has moved more than once, it isn't eligible for en passant
         if pieces[ep_ID].last_moved!=turn-1: continue               # Unless victim was last moved during the previous turn, abort
         legal.append((t_col,t_row))                                 # If the move got through all that crap, it's a lucky winner!  Add it to legal set

      return set(legal)

#---KNIGHT----------------------------------------

class knight(piece):                                                 # Define the knight
   def typ_val(self):
      self.type='n'
      self.value=3                                                   # Knight's value is 3

   def get_legal(self):                                              # Define legal moveset for a knight:
      legal=[]
      for test in n_directions:                                      # For each possible knight move (defined in global variables)
         t_col=self.col+test[0]                                      # Fetch column and row of knight move
         t_row=self.row+test[1]
         if not on_board(t_col,t_row): continue                      # If square if off the board, abort
         if board[t_col][t_row]==None:                               # If square is empty, add to legal move set
            legal.append((t_col,t_row))
         else:
            if pieces[board[t_col][t_row]].colour==self.colour:      # If square occupied by friendly piece, abort
               continue
            else:                                                    # If square occupied by enemy piece, add to legal move set
               legal.append((t_col,t_row))
               
      return set(legal)

#---BISHOP----------------------------------------

class bishop(piece):                                                 # Define the bishop
   def typ_val(self):
      self.type='b'
      self.value=3                                                   # Bishop's value is 3

   def get_legal(self):                                              # Define legal moveset for a bishop:
      dirs=b_directions                                              # Fetch move directions for bishop
      legal=get_legal_lin(dirs,self.colour,self.row,self.col)        # Scan these directions for legal moves
      return set(legal)

#---ROOK------------------------------------------

class rook(piece):                                                   # Define the rook
   def typ_val(self):
      self.type='r'
      self.value=5                                                   # Rook's value is 5

   def get_legal(self):                                              # Define legal moveset for a rook:
      dirs=r_directions                                              # Fetch move directions for rook
      legal=get_legal_lin(dirs,self.colour,self.row,self.col)        # Scan these directions for legal moves 
      return set(legal)

#---QUEEN-----------------------------------------

class queen(piece):                                                  # Define the queen
   def typ_val(self):
      self.type='q'
      self.value=9                                                   # Queen's value is 5

   def get_legal(self):                                              # Define legal moveset for a queen:
      dirs=r_directions+b_directions                                 # Fetch move directions for queen
      legal=get_legal_lin(dirs,self.colour,self.row,self.col)        # Scan these directions for legal moves
      return set(legal)

#---KING------------------------------------------

class king(piece):                                                   # Define the king
   def typ_val(self):
      self.type='k'
      self.value=0                                                   # King's value is undefined (so, 0)

   def get_legal(self):                                              # Define legal moveset for a king:
      legal=[]

      #-----Normal move (1 in any direction)-
      
      dirs=r_directions+b_directions                                 # Fetch move directions for king
      lin=get_legal_lin(dirs,self.colour,self.row,self.col,maxstep=1)# Scan these directions for legal moves
      legal=legal+lin                                                # Add these to the legal set

      #-----Castle Kingside------------------

      for i in range(1):                                             # Create minimal loop so I can use break... it's sloppy but I don't care :)
         if self.last_moved!=0: break                                # If King has previously moved, abort
         castling_rook=self.colour+'_r1'                             # Fetch ID string of kingside rook
         h=homerow[self.colour]                                      # Fetch home row of player
         if pieces[castling_rook].taken: break                       # If the rook is taken, abort
         if pieces[castling_rook].last_moved!=0: break               # If the rook has previously moved, abort
         if board[1][h]!=None: break                                 # If either intervening squares are occupied, abort
         if board[2][h]!=None: break
         if cell_in_check(self.colour,(2,h)): break                  # If king would move through check, abort
         if check_check(self.colour): break                          # If king is already in check, abort
         legal.append((1,h))                                         # Add kingside castle to legal set

      #-----Castle Queenside-----------------

      for i in range(1):
         if self.last_moved!=0: break                                # If King has previously moved, abort
         castling_rook=self.colour+'_r2'                             # Fetch ID string of queenside rook
         h=homerow[self.colour]                                      # Fetch home row of player
         if pieces[castling_rook].taken: break                       # If the rook is taken, abort
         if pieces[castling_rook].last_moved!=0: break               # If the rook has previously moved, abort
         if board[4][h]!=None: break                                 # If any of the 3 intervening squares are occupied, abort
         if board[5][h]!=None: break
         if board[6][h]!=None: break
         if cell_in_check(self.colour,(4,h)): break                  # If king would move through check, abort
         if check_check(self.colour): break                          # If king is already in check, abort
         legal.append((5,h))                                         # Add queenside castle to legal set

      return set(legal)

#-------------------------------------------------

# Capital letter = Piece Type ID:
#
# King
# Queen
# Rook
# kNight
# Bishop
# Pawn

#-----Setup the stats-----------------------------------------------------

turn=0                                                               # Setup turn
turn_player=None                                                     # Initially it is neither payer's turn
taken_this_turn=None                                                 # No pieces have been taken in turn 0
piece_this_turn=None                                                 # No piece type has been used in turn 0
score={ 'w' : 0, 'b' : 0 }                                           # Both players start with no score

#-----Setup the board-----------------------------------------------------

pieces={ 'b_r1': rook(0,0,'b','b_r1'),                               # Initialise all the major pieces, black at the top of the board
         'b_n1': knight(1,0,'b','b_n1'),
         'b_b1': bishop(2,0,'b','b_b1'),
         'b_k' : king(3,0,'b','b_k'),
         'b_q1': queen(4,0,'b','b_q1'),
         'b_b2': bishop(5,0,'b','b_b2'),
         'b_n2': knight(6,0,'b','b_n2'),
         'b_r2': rook(7,0,'b','b_r2'),

         'w_r1': rook(0,7,'w','w_r1'),
         'w_n1': knight(1,7,'w','w_n1'),
         'w_b1': bishop(2,7,'w','w_b1'),
         'w_k' : king(3,7,'w','w_k'),
         'w_q1': queen(4,7,'w','w_q1'),
         'w_b2': bishop(5,7,'w','w_b2'),
         'w_n2': knight(6,7,'w','w_n2'),
         'w_r2': rook(7,7,'w','w_r2')
       }

for i in range(8):                                                   # Initialise the pawns
   bpos=cols_ids[i]+'2'                                              # Construct the position of each black pawn
   wpos=cols_ids[i]+'7'                                              # Construct the position of each white pawn
   pieces['b_p'+str(i+1)]=pawn(i,1,'b','b_p'+str(i+1))               # Initialise each black pawn
   pieces['w_p'+str(i+1)]=pawn(i,6,'w','w_p'+str(i+1))               # Initialise each white pawn

#-----Setup the Screen----------------------------------------------------

def header():                                                        # Define the header; major part of the display including the board and stats

   clear()
   print ' -------------------------'
   print ' -      Chess Game!      -'
   print ' -------------------------'
   print ''
   print ' Score: White-'+'{:2}'.format(str(score['w']))+'    Black-'+str(score['b'])  # Print scores
   print ''
   print ' Turn: '+'{:4}'.format(str((turn+1)/2))+( '  ('+col_to_text(turn_player)+'\'s move)' if turn_player!=None else '' )  # Print turn: stored turn / 2
   print ''

   print '     a   b   c   d   e   f   g   h'                        # Print column identifiers
   for j in range(8):                                                # For each row:
      print '   +---+---+---+---+---+---+---+---+'                   # Print row separator
      rstr=' '+str(j+1)+' |'
      for i in range(8):                                             # For each column:
         if board[i][j]==None:
            rstr+='   '                                              # If cell is empty, print nothing
         else:
            print_piece=pieces[board[i][j]].type                     # If cell full, fetch type of piece in cell
            if pieces[board[i][j]].colour=='w':
               print_piece=print_piece.upper()                       # If player is white, print capital letter.  Else, lower case
            rstr+=' '+print_piece+' '                                # If cell is occupied, print piece type ID
         rstr+='|'
      print rstr
   print '   +---+---+---+---+---+---+---+---+'
   print ''
   print ' -------------------------------------'
   w_taken='  W: '
   b_taken='  B: '
   for ID in pieces:                                                 # For all pieces:
      piece=pieces[ID]
      if piece.taken:                                                # If piece is taken:
         if piece.colour=='w':
            w_taken=w_taken+piece.type.upper()+' '                   # If piece is white, add it to white's graveyard
         else:
            b_taken=b_taken+piece.type+' '                           # If piece is black, add it to black's graveyard
   print w_taken                                                     # Print white's graveyard
   print ' -------------------------------------'
   print b_taken                                                     # Print black's graveyard
   print ' -------------------------------------'
   print ''                                                          #V Print current player and some instrcutions
   if turn_player!=None: print ' \'Resign\' to quit, \'Draw\' to offer Draw'; print ''; print ''
   if turn_player=='w': print ' White Player (Uppercase Letters):'; print ''
   elif turn_player=='b': print ' Black Player (Lowercase Letters):'; print ''

         

#-----Turn Sequence-------------------------------------------------------

def do_turn(colour):

   global turn_player                                                # Make turn_player, player_this_turn and piece_this_turn usable outside of do_turn
   global taken_this_turn
   global piece_this_turn

   turn_player=colour                                                # Set turn_player to colour passed into do_turn
   taken_this_turn=None                                              # No piece has been selected or taken at this point
   piece_this_turn=None

   special_move=None                                                 # Assume the player won't do a special move

   while True:

      header()                                                       # Refresh screen
      move_start=raw_input(' Select Piece to Move:       ')          # Ask user what they want to do
      print ''

      #-----Check for Resign-----------------
      
      if move_start.lower()=='resign':                               # If the player resigned, end the game
         return not_(colour),'Resigned'                              # Note that the inactive player won through resignation

      #-----Check for Draw Offer-------------
      
      if move_start.lower() in ('draw','offer draw','offer_draw','offerdraw'): # If the player called for a draw:
         header()
         print ' '+col_to_text(colour)+' Player has offered a Draw!'
         print ''
         while True:
            draw_response=raw_input(' '+col_to_text(not_(colour))+ ' Player: Would you like to accept the Draw? [Y/N]: ').lower()
            if draw_response in ('y','yes'):                         # If other player accepts the draw, endthe game
               return colour,'Draw'                                  # Note that the active player offered the draw that was accepted
            else:
               header()
               print ' '+col_to_text(colour)+'\'s offer to Draw was rejected!'
               print ''
               print ' [Enter to Continue]'
               raw_input('')
               header()
               break
         continue

      #-----Fetch Piece Square---------------
         
      try:
         row,col=square_to_cell(move_start)                          # Try and convert user input to a cell
      except:
         print ' Invalid Square! [Enter to Continue]'                # If it fails, scold them heartily.
         raw_input('')
         continue
      selected=board[row][col]                                       # Save the ID of the selected piece
      if selected==None:                                             # If no piece in cell, moan at player
         print ' No Piece in Square! [Enter to Continue]'
         raw_input('')
         continue
      if pieces[selected].colour!=colour:
         print ' No',col_to_text(colour),'piece in Square! [Enter to Continue]' # If player tries to select the other player's piece, moan
         raw_input('')
         continue
      piece_this_turn=pieces[selected].type                          # Save the type of the selected piece
      print '',piece_to_text(piece_this_turn),'in',move_start.upper(),'selected!'
      print ''

      #-----Fetch Move Square----------------

      move_end=raw_input(' Select Square to Move into: ')            # Fetch move endpoint from user
      print ''
      try:
         square_to_cell(move_end)
      except:
         print ' Invalid Square! [Enter to Continue]'                # If they give an invalid square, try again from the top...
         raw_input('')
         continue
      m_s_c,m_s_r=square_to_cell(move_start)                         # Fetch Move Start Column, Move Start Row
      m_e_c,m_e_r=square_to_cell(move_end)                           # Fetch Move End Column, Move End Row
      
      if into_check(colour,m_s_c,m_s_r,m_e_c,m_e_r):                 # Check if this move would put the player in check
         print ' Illegal move! [Enter to Continue]'                  # Abort if it does
         raw_input('')
         continue
      move_legal=pieces[selected].try_move(move_end)                 # Work out if move is legal

      if move_legal:                                                 # If it is, move to the next step
         break

      else:                                                          # If it isn't, take it from the top
         print ' Illegal move! [Enter to Continue]'
         raw_input('')
         continue

   #-----Check for en Passant----------------

   if piece_this_turn=='p' and taken_this_turn==None and (m_s_c-m_e_c)!=0: # If pawn changed column but didn't take anything, assume en passant
      pieces[board[m_e_c][m_s_r]].take()                             # Take the piece immediately behind the attacking pawn
      board[m_e_c][m_s_r]=None                                       # Have to blank the square manually as take() assumes the piece has been overwritten
      special_move='en_passant'

   #-----Check for castling------------------

   if pieces[selected].type=='k' and (m_s_c,m_s_r) == (3,homerow[colour]): # If selected piece was the king on its starting square, scan for castling
      if (m_e_c,m_e_r) == (1,homerow[colour]):                       # If king moved 2 squares towards kingside, declare kingside castle
         special_move='castle_kingside'
         castling_rook=colour+'_r1'                                  # Work out which rook should move
         rookmove='c'+str(homerow[colour]+1)                         # Work out where the rook should go
         pieces[castling_rook].move(rookmove)                        # Hop the rook over the king
         
      if (m_e_c,m_e_r) == (5,homerow[colour]):                       # If king moved 2 squares towards queenside, declare queenside castle
         special_move='castle_queenside'
         castling_rook=colour+'_r2'                                  # Work out which rook should move
         rookmove='e'+str(homerow[colour]+1)                         # Work out where the rook should go
         pieces[castling_rook].move(rookmove)                        # Hop the rook over the king

   #-----Print outcome of move---------------

   header()

   if special_move=='castle_kingside':                               # If castling happened, state it
      print ' Castled Kingside!'
   elif special_move=='castle_queenside':
      print ' Castled Queenside!'
   else:
      print ' Moved',piece_to_text(piece_this_turn),'to',move_end.upper() # State which piece was moved
      if taken_this_turn!=None:
         print ''                                                    # If something was taken this turn, state that
         print ' Took',piece_to_text(taken_this_turn)+(' en Passant' if special_move=='en_passant' else '')+'!'
   print ''

   print ' [Enter to Continue]'
   raw_input('')

   #-----Check for promotion-----------------

   if piece_this_turn=='p' and m_e_r==homerow[not_(colour)]:         # If a pawn reached the final rank:
      while True:
         header()
         print ' Congratulations!  Pawn reached 8th Rank.'           # Congratulate the player
         print ''                                                    # Ask the player what they want to promote the pawn to
         promo_piece=raw_input(' Choose Piece to Promote Pawn to: ').lower()
         if promo_piece in ['queen','q']:                            # Upgrade pawn to queen
            promo_piece='Queen'
            pieces[selected]=queen(m_e_c,m_e_r,colour,selected)      # Overwrite pawn with new queen
            break
         elif promo_piece in ['rook','r','castle','c']:              # Upgrade pawn to rook
            promo_piece='Rook'
            pieces[selected]=rook(m_e_c,m_e_r,colour,selected)       # Overwrite pawn with new rook
            break
         elif promo_piece in ['bishop','b']:                         # Upgrade pawn to bishop (seriously, why?)
            promo_piece='Bishop'
            pieces[selected]=bishop(m_e_c,m_e_r,colour,selected)     # Overwrite pawn with new bishop
            break
         elif promo_piece in ['knight','k','n']:                     # Upgrade pawn to knight
            promo_piece='Knight'
            pieces[selected]=knight(m_e_c,m_e_r,colour,selected)     # Overwrite pawn with new knight
            break
      header()
      print ' Pawn promoted to '+promo_piece+'!'
      print ''
      print ' [Enter to Continue]'
      raw_input('')

   #-----Check Enemy's Status----------------

   in_check=check_check(not_(colour))                                # Work out if enemy is in check
   is_legal_move=can_move(not_(colour))                              # Work out if enemy has any legal moves

   if is_legal_move and (not in_check):                              # If they aren't in check but do have legal moves, do nothing
      pass
   elif is_legal_move and in_check:                                  # If they are in check and do have legal moves, alert them to this
      header()
      print ' '+col_to_text(not_(colour)),'Player is in Check!'
      print ''
      print ' [Enter to Continue]'
      raw_input('')
   elif (not is_legal_move) and in_check:                            # If they are in check and have no legal moves, declare active player the victor
      return colour,'is in Checkmate!'
   else:
      return colour,'Stalemate'                                      # If they have no legal moves and aren't in check, declare stalemate

   return None
   
#-----Game!---------------------------------------------------------------

header()                                                             # Print introduction
print ''
print ''
print '            -- Welcome! --'
print ''
print '           [Enter] to Play!'
raw_input('')

while winner==None:                                                  # Check nobody has been declared winner
   turn+=1
   winner=do_turn('w')                                               # Do white's turn
   if winner!=None:                                                  # Check nobody has been declared winner
      break
   turn+=1
   winner=do_turn('b')                                               # Do black's turn

turn_player=None                                                     # When the game has been declared over, it is nobody's turn
header()

#-----Check for Stalemate--------------------

if winner[1]=='Stalemate':                                           # If stalemate token has been passed, declare stalemate
   print ''
   print ''
   print '   ***** ',col_to_text(not_(winner[0])),'Player has no legal moves! *****'
   print ''
   print '   *****   Stalemate!   *****'

#-----Check for Mutual Draw------------------

elif winner[1]=='Draw':                                              # If draw token has been passed, declare draw
   print ''
   print ''
   print '   ***** ',col_to_text(not_(winner[0])),'Player accepted a Draw! *****'
   print ''
   print '   *****   Draw!   *****'

#-----Declare Winner-------------------------
   
else:                                                                # If winner token has been passed, declare winner
   print ''
   print ''
   print '   ***** ',col_to_text(not_(winner[0])),' Player '+winner[1]+'! *****'
   print ''
   print '   *****   ',col_to_text(winner[0]),'Player Wins!   *****'

raw_input('')
