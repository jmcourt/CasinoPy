#! /usr/bin/env python

import random
import os
import platform

def clear():
   system=platform.system().lower()
   if system=='linux':
      os.system('clear')
   else:
      os.system('cls')
      

suits=[' of Hearts  ',' of Spades  ',' of Diamonds',' of Clubs   ']
faces=[[str(i),i] for i in range(2,11)]
faces+=[['Ace',1],['Jack',10],['Queen',10],['King',10]]
aces=set(['Ace'+i for i in suits])

def header(turn):
   clear()
   print '-------------------------'
   print '-    BlackJack Game!    -'
   print '-------------------------'
   print ''
   if turn>0:
      for i in range(turn-1):
         print 'Player '+str(i+1)+' stuck!'
         print ''
      print 'Player '+str(turn)+'\'s Turn!'
      print ''
   elif turn==-1:
      print 'GAME OVER!'
      print ''

def stall():
   print 'Press [ENTER] to continue.'
   raw_input('')

def stall_c():
   print '[ENTER] to clear.'
   raw_input('')

#----------------------------------------------------------

class deck:
   def shuffle(self):
      self.number_of_cards=52
      self.cards=[]
      self.cvals=[]

      for i in range(52):
         self.cards.append(faces[i%13][0]+suits[i/13])
         self.cvals.append(faces[i%13][1])

   def draw(self):
      pick=int(random.random()*self.number_of_cards)
      card=self.cards.pop(pick)
      value=self.cvals.pop(pick)
      self.number_of_cards-=1
      return card, value    

#----------------------------------------------------------

class hand:
   def __init__(self,deck):
      self.cards=[]
      self.points=0
      self.stuck=False
      self.busted=False
      if deck!=None:
         self.twist(deck,show=False)
         self.twist(deck,show=False)
         self.show()

   def get_points(self):
      return self.points

   def twist(self,deck,show=True):
      card,value=deck.draw()
      if show:
         print 'You Drew :'
         print ''
         print '{:>18}'.format(card)
         print ''
         stall_c()
      self.cards.append(card)
      self.points+=value

   def stick(self):
      self.stuck=True
      if len(aces & set(self.cards))>0 and self.points<=11:
         self.points+=10
      print 'Stuck!'

   def bust(self):
      self.busted=True
      self.stuck=True
      self.points=0
      print 'Oh snap, you busted!'
      stall()

   def show(self):
      print 'Your Hand Is:'
      print ''
      for i in self.cards:
         print '{:>18}'.format(i)
      print ''
      stall_c()

#----------------------------------------------------------

class split_hand:
   def __init__(self,deck,in_cards,in_points):
      assert len(in_cards)==2
      self.stuck=False
      self.busted=False
      self.points=0
      self.hand1=hand(None)
      self.hand2=hand(None)
      self.hand1.cards=[in_cards[0]]
      self.hand2.cards=[in_cards[1]]
      self.hand1.points=in_points/2
      self.hand2.points=in_points/2
      self.hand1.twist(deck,show=False)
      self.hand2.twist(deck,show=False)

   def get_points(self):
      if not self.hand1.stuck:      
         return self.hand1.get_points()
      elif not self.hand2.stuck:      
         return self.hand2.get_points()
      else:      
         return self.points

   def show(self):
      print 'Your Hands Are:'
      print ''
      for i in self.hand1.cards:
         print '{:>18}'.format(i)
      print ''
      print 'And:'
      print ''
      for i in self.hand2.cards:
         print '{:>18}'.format(i)
      print ''
      stall_c()

   def twist(self,deck):
      card,value=deck.draw()
      print 'You Drew :'
      print ''
      print '{:>18}'.format(card)
      print ''
      stall_c()
      if self.hand1.stuck:
         self.hand2.cards.append(card)
         self.hand2.points+=value
      else:
         self.hand1.cards.append(card)
         self.hand1.points+=value

   def stick(self):
      if not self.hand1.stuck:
         self.hand1.stick()
         if len(aces & set(self.hand1.cards))>0 and self.hand1.points<=11:
            self.hand1.points+=10
         print 'Stuck on hand 1!'
         print ''
         stall()
      else:
         self.hand2.stick()
         if len(aces & set(self.hand2.cards))>0 and self.hand2.points<=11:
            self.hand2.points+=10
         self.points=max(self.hand1.points,self.hand2.points)
         print 'Stuck on hand 2!'
         print ''
         stall()
         self.stuck=True

   def bust(self):
      if not self.hand1.stuck:
         self.hand1.bust()
      else:
         self.hand2.bust()
         self.busted=True
         self.stuck=True
         self.points=max(self.hand1.points,self.hand2.points)

#################################################

header(0)
print 'Press [ENTER] to get started!'
raw_input('')

#################################################

while True:

   header(0)
   try:
      players=int(raw_input('How many players (2-5)? : '))
      assert players>1
      assert players<6
      break
   except: pass

total_scores=[0]*players

play_deck=deck()

while True:

   round_scores=[0]*players
   splitted=[False]*players

   hands={}
   play_deck.shuffle()

   for i in range(players):

      turn=i+1
      can_dd=False

      header(turn)
      stall()

#################################################

      header(turn)
      hands[i]=hand(play_deck)

      options='Twist, Stick or sHow!: '

      if hands[i].cards[0][0]==hands[i].cards[1][0]:
         can_dd=True
         options='Twist, Stick, sHow or sPlit!: '

      header(turn)

      if hands[i].points==11 and len(aces & set(hands[i].cards))>0:
         hands[i].points=22
         print 'Congratulations!  You got blackjack!'
         stall()

      else:
         while not hands[i].stuck:

            option=raw_input(options).lower()
            print ''

            if option in ['stick','s']:
               hands[i].stick()
               can_dd=False
               if splitted[i]:
                  options='Twist, Stick or sHow on Hand 2!: '
            elif option in ['twist','t']:
               hands[i].twist(play_deck)
               can_dd=False
            elif option in ['show','h']:
               hands[i].show()
               can_dd=False
            elif can_dd and option in ['p','split']:
               can_dd=False
               splitted[i]=True
               hands[i]=split_hand(play_deck,hands[i].cards,hands[i].points)
               print 'Split!'
               print ''
               stall()
               options='Twist, Stick or sHow on Hand 1!: '
               header(turn)
               hands[i].show()

            header(turn)

            if hands[i].get_points()>21:
               hands[i].bust()
               if splitted[i]:
                  options='Twist, Stick or sHow on Hand 2!: '

      round_scores[i]=hands[i].points

   print 'ok'

#################################################

   header(-1)
   print 'Round Scores:'
   print ''
   for player in range(players):
      if splitted[player]:
         ddtext=' Split and'
      else:
         ddtext=''
      if round_scores[player]==0:
         print 'Player '+str(player+1)+ddtext+' Busted!'
      elif round_scores[player]>21:
         print 'Player '+str(player+1)+' got Blackjack!'
      else:
         print 'Player '+str(player+1)+ddtext+' scored '+str(round_scores[player])+'!'
   print ''

   stall()
#################################################

   header(-1)

   best=max(round_scores)
   winners=[player for player,p_score in enumerate(round_scores) if p_score==best]
   if best==0:
      print 'Nobody wins!'
   elif len(winners)==1:
      print 'Player '+str(winners[0]+1)+' wins!'
      total_scores[winners[0]]+=1
   else:
      print 'Players '+str([ i+1 for i in winners[:-1]]).strip('[]')+' and '+str(winners[-1]+1)+' tie!'
      for i in winners:
         total_scores[i]+=1

   print ''
   stall()

#################################################

   header(-1)

   print 'Total Scores:'
   print ''
   for player in range(players):
      print 'Player '+str(player+1)+': '+str(total_scores[player])
   print ''
   stall()



