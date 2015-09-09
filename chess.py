#! /usr/bin/env python

from numpy import array

board=array([array([None]*8)]*8)
print board

def square_to_cell(square):                                               # Convery user input to grid location
   try:
      assert len(square)==2
      col,row=square[0],square[1]
      row=int(row)-1
      if col=='a':
         col=0
      elif col=='b':
         col=1
      elif col=='c':
         col=2
      elif col=='d':
         col=3
      elif col=='e':
         col=4
      elif col=='f':
         col=5
      elif col=='g':
         col=6
      elif col=='h':
         col=7
      assert row>=0
      assert row<=7
      assert col>=0
      assert col<=7
      return col,row
   except:
      return None,None

#--------------------------------------------------------

class piece:
   def __init__(self,square,colour,ID):
      self.col,self.row=square_to_cell(square)
      self.taken=False
      self.ID=ID
      self.colour=colour
      board[self.col][self.row]=ID

   def get_legal(self):
      return [],[]

   def move(self,square):
      board[self.col][self.row]=None
      self.col,self.row=square_to_cell(square)
      board[self.col][self.row]=ID

   def take(self):
      self.taken=True
      self.col=None
      self.row=None

   def try_move(self,square):
      trycol,tryrow=square_to_cell(square)
      if trycol in self.get_legal[0] and tryrow in self.get_legal[0]:
         occupant=board[trycol,tryrow]
         if occupant!=None:
            pieces[occupant].take()
         self.move(square)
         return True
      else:
         return False


      

class pawn(piece):
   self.type='p'

class knight(piece):
   self.type='k'

class bishop(piece):
   self.type='b'

class rook(piece):
   self.type='r'

class queen(piece):
   self.type='q'

class king(piece):
   self.type=

# King
# Queen
# Rook
# kNight
# Bishop
# Pawn



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

for i in range(8):
   bpos=cols_ids[i]+'2'
   wpos=cols_ids[i]+'7'
   pieces['b_p'+str(i+1)]=pawn(bpos,'b','b_p'+str(i+1))
   pieces['w_p'+str(i+1)]=pawn(wpos,'w','w_p'+str(i+1))

print board

