#cards: undealt cards.  0th element is on top. This card is appended to end of play_pile.
#play_pile: face-up cards.  0th element is on bottom. last element is the visible one.
#up-piles: Four of them; each suit, from 1 to 13.  0th element is on the bottom.  append to end.
#down-piles: 7 of them, defined by class pile. Initially of length 1-7.
#  Each has N cards down.  Nth element is first up, and can move to another pile.
#  Last element is end of pile, and can play or be played upon.
#
# Save as solitaire002: Arranging elements.
# Need to make 'main' section.  See example in Chat GPT 10/26/24.


#imports
import random

#constants

#class def

class pile:
    def __init__(self, length):
        self.list = [draw(cards) for i in range(length)]
        self.down = length - 1  # Instance variable
        

#functions
        
up_piles = [[] for _ in range(4)]   #initially empty numbered piles to hold A-K of each suit
play_pile = []
cards = [(i+1,j) for i in range(13) for j in range(4)]   #52 cards
random.shuffle(cards)   #shuffled cards

def draw(list):							#function to draw a duple from a list
    a=random.randint(0,len(list)-1)
    return (list.pop(a))

def check_for_up_piles(tup):
    for i in range(4):
        if tup[1] == i:		#suit matches
            if up_piles[i] == []:	#if pile is still empty
                if tup[0] == 1:  #if card is an ace.
                    return(True,i)  #it is the matching ace.
                else:
                    return(False, None)  #right suit, not the ace.
            elif up_piles[i][-1][0] == tup[0]-1:
                return(True,i)
            else:
                return(False, None)
            
    return(False)
    
def move_from_to(list1,i,list2):		#want to add a parameter, and make this more general - should move all elements beyond some given element to new location.
    list2.append(list1.pop(i))
                        
                





  
down_piles= [pile(i+1) for i in range(7)]   #starting piles with 1 to 7 cards.





for _ in range(1):
    while (len(cards) > 0):
        move_from_to(cards,0,play_pile)   #move top element of cards to play_pile last element.
        chck = check_for_up_piles(play_pile[-1])
        if chck[0]:
            move_from_to(play_pile,-1,up_piles[chck[1]])
    #print(up_piles, len(cards))

    cards = play_pile
    play_pile = []
    

    
        
for i in range(4):
    print(up_piles[i])
