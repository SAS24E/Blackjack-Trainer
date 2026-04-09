import random
from card import Card
#########################################################################################################################################################################
# Deck class
# Attributes: cards (a list of Card objects representing the deck)
# Methods: create_deck (creates a standard 52-card deck and shuffles it randomly), deal_card
#########################################################################################################################################################################
class Deck:
    def __init__(self):
        self.cards = self.create_deck()

    # =============================
    # create_deck method
    # creates a standard 52-card deck and shuffles it randomly
    # returns the shuffled deck
    # =============================
    def create_deck(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        deck = []

        for suit in suits:
            for rank in ranks:
                deck.append(Card(rank, suit))

        random.shuffle(deck)
        return deck

    # =============================
    # deal_card method
    # removes and returns the top card from the deck
    # =============================
    def deal_card(self):
        return self.cards.pop()

