class Card:
    """A single playing card."""
    # Card definitions
    FACE_CARD_RANKS = {"jack", "queen", "king"}
    SUITS = ("hearts", "diamonds", "clubs", "spades")
    RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace")

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
