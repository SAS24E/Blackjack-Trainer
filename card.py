class Card:
    """A single playing card."""

    FACE_CARD_RANKS = {"jack", "queen", "king"}

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank.capitalize()} of {self.suit.capitalize()}"

    def value(self):
        """Return the blackjack value for this card."""
        if self.rank in self.FACE_CARD_RANKS:
            return 10
        if self.rank == "ace":
            return 11
        return int(self.rank)
