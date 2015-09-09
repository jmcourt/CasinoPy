#! /usr/bin/env python

from numpy import array
import platform
import os

#-----Create the Board----------------------------------------------------

board=array([array([None]*8)]*8)
turn=0
turn_player=''

#-----Basic Function Definitions------------------------------------------

def square_to_cell(square):                                               # Convert user input to grid location
   try:
      assert len(square)==2
      col,row=square[0],square[1]
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

   except:

      return None,None

def clear():                                                              # Fetch operating system for the sake of system commands
   system=platform.system().lower()
   if system=='windows':
      os.system('cls')
   else:
      os.system('clear')

#-----Define Piece Superclass---------------------------------------------

class piece:
   def __init__(self,square,colour,ID):
      self.col,self.row=square_to_cell(square)
      self.taken=False
      self.ID=ID
      self.typ_val()
      self.colour=colour
      self.last_moved=0
      board[self.col][self.row]=ID

   def typ_val(self):
      self.value=0
      self.type=None

   def get_legal(self):
      return []

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

   def try_move(self,square):                                             # Check if a move is allowed and, if so, do it.
      trycol,tryrow=square_to_cell(square)
      if (trycol,tryrow) in self.get_legal():
         self.move(square)
         return True
      else:
         return False

#-----Define Pieces-------------------------------------------------------

class pawn(piece):
   def typ_val(self):
      self.type='p'
      self.value=1

class knight(piece):
   def typ_val(self):
      self.type='n'
      self.value=3

class bishop(piece):
   def typ_val(self):
      self.type='b'
      self.value=3

class rook(piece):
   def typ_val(self):
      self.type='r'
      self.value=5

class queen(piece):
   def typ_val(self):
      self.type='q'
      self.value=9

class king(piece):
   def typ_val(self):
      self.type='k'
      self.value=0

# King
# Queen
# Rook
# kNight
# Bishop
# Pawn

#-----Setup the board-----------------------------------------------------

pieces={ 'b_r1': rook('a1','b','b_r1'),
         'b_n1': knight('b1','b','b_n1'),
         'b_b1': bishop('c1','b','b_b1'),
         'b_k' : king('d1','b','b_k'),
         'b_q1': queen('e1','b','b_q1'),
         'b_b2': bishop('f1','b','b_b2'),
         'b_n2': knight('g1','b','b_n2'),
         'b_r2': rook('h1','b','b_r2'),

         'w_r1': rook('a8','w','w_r1'),
         'w_n1': knight('b8','w','w_n1'),
         'w_b1': bishop('c8','w','w_b1'),
         'w_k' : king('d8','w','w_k'),
         'w_q1': queen('e8','w','w_q1'),
         'w_b2': bishop('f8','w','w_b2'),
         'w_n2': knight('g8','w','w_n2'),
         'w_r2': rook('h8','w','w_r2')
       }

cols_ids=['a','b','c','d','e','f','g','h']

for i in range(8):                                                        # Do the pawns
   bpos=cols_ids[i]+'2'
   wpos=cols_ids[i]+'7'
   pieces['b_p'+str(i+1)]=pawn(bpos,'b','b_p'+str(i+1))
   pieces['w_p'+str(i+1)]=pawn(wpos,'w','w_p'+str(i+1))

#-----Setup the stats-----------------------------------------------------

score={ 'w' : 0, 'b' : 0 }

#-----Setup the Screen----------------------------------------------------

def header():

   clear()
   print '-------------------------'
   print '-      Chess Game!      -'
   print '-------------------------'
   print ''
   print 'Score: White-'+'{:2}'.format(str(score['b']))+'    Black-'+str(score['w'])
   print ''
   print 'Turn: '+(turn+'  ('+turn_player+'\'s move)' if turn>0 else '')
   print ''

   for j in range(8):
      print '   +---+---+---+---+---+---+---+---+'
      rstr='   |'
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
   w_taken='     '
   b_taken='     '
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

header()




