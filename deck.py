import random

from card import Card


class Deck:
    """A shuffled standard 52-card deck."""

    # Card definitions
    SUITS = ("hearts", "diamonds", "clubs", "spades")
    RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace")

    # Deck lifecycle
    def __init__(self):
        self.cards = self.create_deck()

    def create_deck(self):
        """Create and shuffle a fresh deck."""
        deck = [Card(rank, suit) for suit in self.SUITS for rank in self.RANKS]
        random.shuffle(deck)
        return deck

    def deal_card(self):
        """Remove and return the top card."""
        return self.cards.pop()
