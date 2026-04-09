import random

player_in = True
dealer_in = True

# deck of cards
deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A', 'J', 'Q', 'K', 'A', 'J', 'Q', 'K', 'A', 'J', 'Q', 'K', 'A']
player_hand = []
dealer_hand = []

# deal the cards
def deal_card(turn):
    card = random.choice(deck) # selects a random card
    turn.append(card) # random card gets appened to whoevers turn it is.
    deck.remove(card) # Once that happens we remove card from deck

# calculate the total of the hand

def total(turn):
    total = 0
    face = ['J', 'Q', 'K']
    for card in turn: # for every card in turn  
        if card in range(1, 11): # if the card is in the range 1-10 
            total += card # add card to total
        elif card in face: 
            total += 10
        else:
            if total > 11:
                total += 1
            else:
                total += 11
    return total

# check for winner
def reveal_dealer_hand():
    if len(dealer_hand) == 2:     # if length of dealer hand equals 2 return the current hand
        return dealer_hand[0] 
    elif len(dealer_hand) > 2: # else if the length of dealer hand is greater than 2 return current hand 
        return dealer_hand[0], dealer_hand[1] # we return the first and second card in the dealer_hand??? Confused about this part.


# game loop (deal the cards)
for _ in range(2):
    deal_card(dealer_hand)
    deal_card(player_hand)
    
while player_in or dealer_in:
    print(f"Dealer Has {reveal_dealer_hand()} and X")
    print(f"You have {player_hand} for a total of {total(player_hand)}")
    if player_in:
        stay_or_hit = input("1: Stay\n: 2: Hit\n")
    if total(dealer_hand) > 16:  # Dealer stands on soft 17
        dealer_in = False
    else:
        deal_card(dealer_hand)
    if stay_or_hit == '1':
        player_in = False
    else:
        deal_card(player_hand)
    if total(player_hand) >= 21:
        break
    elif total(dealer_hand) >= 21:
        break

if total(player_hand) == 21:
    print(f"\nYou have {player_hand} for a total of {total(player_hand)} and the dealer has {dealer_hand} for a total of {total(dealer_hand)}")
    print("Blackjack! You Win!")
elif total(dealer_hand) == 21:
    print(f"\nYou have {player_hand} for a total of {total(player_hand)} and the dealer has {dealer_hand} for a total of {total(dealer_hand)}")
    print("Blackjack! Dealer wins!")
elif total(player_hand) > 21:
    print(f"\nYou have {player_hand} for a total of {total(player_hand)} and the dealer has {dealer_hand} for a total of {total(dealer_hand)}")
    print("You bust! Dealer wins!")
elif total(dealer_hand) > 21:
    print(f"\nYou have {player_hand} for a total of {total(player_hand)} and the dealer has {dealer_hand} for a total of {total(dealer_hand)}")
    print("Dealer busts! You win!")
elif 21 - total(dealer_hand) < 21 - total(player_hand):
    print(f"\nYou have {player_hand} for a total of {total(player_hand)} and the dealer has {dealer_hand} for a total of {total(dealer_hand)}")
    print("Dealer wins!")
elif 21 - total(dealer_hand) > 21 - total(player_hand):
    print(f"\nYou have {player_hand} for a total of {total(player_hand)} and the dealer has {dealer_hand} for a total of {total(dealer_hand)}")
    print("You Win!")