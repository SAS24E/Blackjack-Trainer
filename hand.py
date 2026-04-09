class Hand:
    """A blackjack hand."""

    # Hand lifecycle
    def __init__(self):
        self.cards = []

    # Hand behavior
    def add_card(self, card):
        """Add a card to the hand."""
        self.cards.append(card)

    def value(self):
        """Calculate the best blackjack value for the hand."""
        total = 0
        aces = 0

        for card in self.cards:
            total += card.value()
            if card.rank == "ace":
                aces += 1

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    def is_busted(self):
        """Return True when the hand is over 21."""
        return self.value() > 21

    def is_blackjack(self):
        """Return True for a two-card 21."""
        return self.value() == 21 and len(self.cards) == 2
