import random

from card import Card


class Deck:
    """A shuffled standard 52-card deck."""

    # Deck lifecycle
    def __init__(self):
        self.cards = self.create_deck()

    def create_deck(self):
        """Create and shuffle a fresh deck."""
        deck = [Card(rank, suit) for suit in Card.SUITS for rank in Card.RANKS]
        random.shuffle(deck)
        return deck

    def deal_card(self):
        """Remove and return the top card."""
        return self.cards.pop()
