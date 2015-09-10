#! /usr/bin/env python

from copy import copy
from numpy import array
import platform
import os

#-----Create the Board----------------------------------------------------

board=array([array([None]*8)]*8)

#-----Set Global Variables------------------------------------------------

turn=0
turn_player=None
taken_this_turn=None

winner=None

b_directions=[(1,1),(1,-1),(-1,1),(-1,-1)]
r_directions=[(1,0),(0,1),(-1,0),(0,-1)]
n_directions=[(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]

#-----Basic Function Definitions------------------------------------------

def square_to_cell(square):                                               # Convert user input to grid location
   assert len(square)==2
   col,row=square[0],square[1]
   col=col.lower()
   row=int(row)-1

   if col=='a':   col=0
   elif col=='b': col=1
   elif col=='c': col=2
   elif col=='d': col=3
   elif col=='e': col=4
   elif col=='f': col=5
   elif col=='g': col=6
   elif col=='h': col=7

   assert row>=0
   assert row<=7
   assert col>=0
   assert col<=7

   return col,row


def clear():                                                              # Fetch operating system for the sake of system commands
   system=platform.system().lower()
   if system=='windows':
      os.system('cls')
   else:
      os.system('clear')

def piece_to_text(pID):
   if pID=='k': return 'King'
   elif pID=='q': return 'Queen'
   elif pID=='r': return 'Rook'
   elif pID=='b': return 'Bishop'
   elif pID=='n': return 'Knight'
   elif pID=='p': return 'Pawn'
   else: return 'None'

def col_to_text(cID):
   if cID=='w': return 'White'
   elif cID=='b': return 'Black'
   else: return 'None'

def not_(player):
   if player=='w': return 'b'
   else: return 'w'

#-----Check Checkers------------------------------------------------------

def check_check(colour):

   king_loc=pieces[colour+'_k'].col,pieces[colour+'_k'].row
   danger_squares=set([])
   for ID in pieces:
      if (not pieces[ID].taken) and (pieces[ID].colour != colour):
         danger_squares=danger_squares | pieces[ID].get_legal()

   ##########

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

   if king_loc in danger_squares:
      return True
   else:
      return False


def into_check(colour,f_col,f_row,t_col,t_row):

   save_id_f=board[f_col][f_row]
   save_id_t=board[t_col][t_row]

   if save_id_t!=None:
      pieces[save_id_t].row=None
      pieces[save_id_t].col=None
      pieces[save_id_t].taken=True

   pieces[save_id_f].row=t_row
   pieces[save_id_f].col=t_col

   board[f_col][f_row]=None
   board[t_col][t_row]=save_id_f

   is_in_check=check_check(colour)

   pieces[save_id_f].row=f_row
   pieces[save_id_f].col=f_col

   if save_id_t!=None:
      pieces[save_id_t].row=t_row
      pieces[save_id_t].col=t_col
      pieces[save_id_t].taken=False

   board[f_col][f_row]=save_id_f
   board[t_col][t_row]=save_id_t

   return is_in_check

def can_move(colour):
   is_legal_move=False

   for ID in pieces:
      if (pieces[ID].colour!=colour) or (pieces[ID].taken):
         continue
      legal_s_c=pieces[ID].col
      legal_s_r=pieces[ID].row
      moves=pieces[ID].get_legal()
      for move in moves:
         legal_e_c=move[0]
         legal_e_r=move[1]
         is_legal_move=not into_check(colour,legal_s_c,legal_s_r,legal_e_c,legal_e_r)
         if is_legal_move:
            break
      if is_legal_move:
         break

   return is_legal_move


#-----Define Piece Superclass---------------------------------------------

class piece:
   def __init__(self,col,row,colour,ID):
      self.col,self.row=col,row
      if row==None:
         self.taken=True
      else:
         self.taken=False
      self.ID=ID
      self.typ_val()
      self.colour=colour
      self.last_moved=turn
      board[self.col][self.row]=ID

   def typ_val(self):
      self.value=0
      self.type=None

   def get_legal(self):
      return set([])

   def move(self,square):
      board[self.col][self.row]=None
      self.col,self.row=square_to_cell(square)
      if board[self.col][self.row]!=None:                                 # Take piece if on the square you're trying to move to
         pieces[board[self.col][self.row]].take()
      board[self.col][self.row]=self.ID
      self.last_moved=turn

   def take(self):                                                        # What to do if this piece is taken
      self.taken=True
      self.col=None
      self.row=None
      score[self.colour]+=self.value
      global taken_this_turn
      taken_this_turn=self.type

   def try_move(self,square):                                             # Check if a move is allowed and, if so, do it.
      trycol,tryrow=square_to_cell(square)
      if (trycol,tryrow) in self.get_legal():
         self.move(square)
         return True
      else:
         return False

#-----Define Pieces-------------------------------------------------------


#---PAWN------------------------------------

class pawn(piece):
   def typ_val(self):
      self.type='p'
      self.value=1

   def get_legal(self):
      legal=[]
      return set([(0,0)])

#---KNIGHT----------------------------------

class knight(piece):
   def typ_val(self):
      self.type='n'
      self.value=3

   def get_legal(self):
      legal=[]
      for test in n_directions:
         t_col=self.col+test[0]
         t_row=self.row+test[1]
         if t_col>7: continue
         if t_row>7: continue
         if t_col<0: continue
         if t_row<0: continue
         if board[t_col][t_row]==None:
            legal.append((t_col,t_row))
         else:
            if pieces[board[t_col][t_row]].colour==self.colour:           # If victim piece is player's colour, cant take it
               continue
            else:
               legal.append((t_col,t_row))
      return set(legal)


#---BISHOP----------------------------------

class bishop(piece):
   def typ_val(self):
      self.type='b'
      self.value=3

   def get_legal(self):
      legal=[]
      for test in b_directions:
         steps=1
         while True:
            t_col=self.col+test[0]*steps
            t_row=self.row+test[1]*steps
            if t_col>7: break
            if t_row>7: break
            if t_col<0: break
            if t_row<0: break
            if board[t_col][t_row]!=None:
               if pieces[board[t_col][t_row]].colour==self.colour:           # If victim piece is player's colour, cant take it
                  break
               else:
                  legal.append((t_col,t_row))                                # Can take enemy piece though.  Either way ends the run
                  break
            else:
               legal.append((t_col,t_row))
               steps+=1

      return set(legal)


#---ROOK------------------------------------

class rook(piece):
   def typ_val(self):
      self.type='r'
      self.value=5

   def get_legal(self):
      legal=[]
      for test in r_directions:
         steps=1
         while True:
            t_col=self.col+test[0]*steps
            t_row=self.row+test[1]*steps
            if t_col>7: break
            if t_row>7: break
            if t_col<0: break
            if t_row<0: break
            if board[t_col][t_row]!=None:
               if pieces[board[t_col][t_row]].colour==self.colour:           # If victim piece is player's colour, cant take it
                  break
               else:
                  legal.append((t_col,t_row))                                # Can take enemy piece though.  Either way ends the run
                  break
            else:
               legal.append((t_col,t_row))
               steps+=1

      return set(legal)

#---QUEEN-----------------------------------

class queen(piece):
   def typ_val(self):
      self.type='q'
      self.value=9

   def get_legal(self):
      legal=[]
      for test in r_directions+b_directions:
         steps=1
         while True:
            t_col=self.col+test[0]*steps
            t_row=self.row+test[1]*steps
            if t_col>7: break
            if t_row>7: break
            if t_col<0: break
            if t_row<0: break
            if board[t_col][t_row]!=None:
               if pieces[board[t_col][t_row]].colour==self.colour:           # If victim piece is player's colour, cant take it
                  break
               else:
                  legal.append((t_col,t_row))                                # Can take enemy piece though.  Either way ends the run
                  break
            else:
               legal.append((t_col,t_row))
               steps+=1

      return set(legal)


#---KING------------------------------------

class king(piece):
   def typ_val(self):
      self.type='k'
      self.value=0

   def get_legal(self):
      legal=[]
      for test in r_directions+b_directions:
         t_col=self.col+test[0]
         t_row=self.row+test[1]
         if t_col>7: continue
         if t_row>7: continue
         if t_col<0: continue
         if t_row<0: continue
         if board[t_col][t_row]==None:
            legal.append((t_col,t_row))
         else:
            if pieces[board[t_col][t_row]].colour==self.colour:           # If victim piece is player's colour, cant take it
               continue
            else:
               legal.append((t_col,t_row))                                # Can take enemy piece though.  Either way ends the run
               continue
      return set(legal)

#-------------------------------------------

# King
# Queen
# Rook
# kNight
# Bishop
# Pawn

#-----Setup the board-----------------------------------------------------

pieces={ 'b_r1': rook(0,0,'b','b_r1'),
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

cols_ids=['a','b','c','d','e','f','g','h']

for i in range(8):                                                        # Do the pawns
   bpos=cols_ids[i]+'2'
   wpos=cols_ids[i]+'7'
   pieces['b_p'+str(i+1)]=pawn(i,1,'b','b_p'+str(i+1))
   pieces['w_p'+str(i+1)]=pawn(i,6,'w','w_p'+str(i+1))

#-----Setup the stats-----------------------------------------------------

score={ 'w' : 0, 'b' : 0 }

#-----Setup the Screen----------------------------------------------------

def header():

   clear()
   print ' -------------------------'
   print ' -      Chess Game!      -'
   print ' -------------------------'
   print ''
   print ' Score: White-'+'{:2}'.format(str(score['b']))+'    Black-'+str(score['w'])
   print ''
   print ' Turn: '+'{:4}'.format(str(turn))+( '  ('+col_to_text(turn_player)+'\'s move)' if turn_player!=None else '' )
   print ''

   print '     a   b   c   d   e   f   g   h'
   for j in range(8):
      print '   +---+---+---+---+---+---+---+---+'
      rstr=' '+str(j+1)+' |'
      for i in range(8):
         if board[i][j]==None:
            rstr+='   '
         else:
            print_piece=pieces[board[i][j]].type
            if pieces[board[i][j]].colour=='w':
               print_piece=print_piece.upper()
            rstr+=' '+print_piece+' '
         rstr+='|'
      print rstr
   print '   +---+---+---+---+---+---+---+---+'
   print ''
   print ' -------------------------------------'
   w_taken='  W: '
   b_taken='  B: '
   for ID in pieces:
      piece=pieces[ID]
      if piece.taken:
         if piece.colour=='w':
            w_taken=w_taken+piece.type.upper()+' '
         else:
            b_taken=b_taken+piece.type+' '
   print w_taken
   print ' -------------------------------------'
   print b_taken
   print ' -------------------------------------'
   print ''
   if turn_player=='w': print ' White Player (Uppercase Letters):'; print ''
   elif turn_player=='b': print ' Black Player (Lowercase Letters):'; print ''
         

#-----Turn Sequence-------------------------------------------------------

def do_turn(colour):

   global turn_player
   global taken_this_turn

   turn_player=colour
   taken_this_turn=None

   while True:

      #---Fetch Piece Square----------------------------

      header()
      move_start=raw_input(' Select Piece to Move or Resign:  ')
      print ''
      if move_start.lower()=='resign':
         return not_(colour),'Resigned'                                         # Note that the inactive player won through resignation
      try:
         row,col=square_to_cell(move_start)
      except:
         print ' Invalid Square! [Enter to Continue]'
         raw_input('')
         continue
      selected=board[row][col]
      if selected==None:
         print ' No Piece in Square! [Enter to Continue]'
         raw_input('')
         continue
      if pieces[selected].colour!=colour:
         print ' No',col_to_text(colour),'piece in cell! [Enter to Continue]'
         raw_input('')
         continue
      print '',piece_to_text(pieces[selected].type),'in',move_start.upper(),'selected!'
      print ''

      #---Fetch Move Square-----------------------------

      move_end=raw_input(' Select Square to Move into:      ')
      print ''
      try:
         square_to_cell(move_end)
      except:
         print ' Invalid Square! [Enter to Continue]'
         raw_input('')
         continue
      m_s_c,m_s_r=square_to_cell(move_start)
      m_e_c,m_e_r=square_to_cell(move_end)
      if into_check(colour,m_s_c,m_s_r,m_e_c,m_e_r):
         print ' Illegal move! [Enter to Continue]'
         raw_input('')
      move_legal=pieces[selected].try_move(move_end)

      if move_legal:
         break

      else:
         print ' Illegal move! [Enter to Continue]'
         raw_input('')
         continue

   header()

   print ' Moved',piece_to_text(pieces[selected].type),'to',move_end.upper()
   
   if taken_this_turn!=None:
      print ''
      print ' Took',piece_to_text(taken_this_turn)+'!'
   print ''
   print ' [Enter to Continue]'

   raw_input('')

   in_check=check_check(not_(colour))
   is_legal_move=can_move(not_(colour))

   if is_legal_move and (not in_check):
      pass
   elif is_legal_move and in_check:
      header()
      print colour_to_text(not_(colour)),'is in Check!'
      print ''
      print '[Enter] to continue.'
   elif (not is_legal_move) and in_check:
      return colour,'is in Checkmate!'
   else:
      return colour,'Stalemate1'

   return None
   

#-----Game!---------------------------------------------------------------

header()
print ''
print ''
print '            -- Welcome! --'
print ''
print '           [Enter] to Play!'
raw_input('')

while winner==None:
   turn+=1
   winner=do_turn('w')
   if winner!=None:
      break
   winner=do_turn('b')

turn_player=None
header()
if winner[1]!='Stalemate1':
   print ''
   print ''
   print '   *****',col_to_text(not_(winner[0])),'Player '+winner[1]+'! *****'
   print ''
   print '   *****  ',col_to_text(winner[0]),'Player Wins!   *****'
else:
   print ''
   print ''
   print '   *****',col_to_text(not_(winner[0])),'Player has no legal moves! *****'
   print ''
   print '   *****  Stalemate!   *****'

raw_input('')
