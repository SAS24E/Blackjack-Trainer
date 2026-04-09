from card import Card
#########################################################################################################################################################################
# Hand Class
# Attributes: cards (a list of Card objects in the hand)
# Methods: add_card, value, is_busted, is_blackjack
#########################################################################################################################################################################
class Hand:
    def __init__(self):
        self.cards = []

    # =============================
    # add_card method
    # adds a card to the hand
    # =============================
    def add_card(self, card):
        self.cards.append(card)

    # =============================
    # value method
    # calculates the total value of the hand according to blackjack rules
    # =============================
    def value(self):
        total = 0
        aces = 0

        for card in self.cards:
            total += card.value()
            if card.rank == 'ace':
                aces += 1

        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    # =============================
    # is_busted method
    # returns True if the hand value exceeds 21
    # =============================
    def is_busted(self):
        return self.value() > 21

    # =============================
    # is_blackjack method
    # returns True if the hand is a blackjack (21 with exactly two cards)
    # =============================
    def is_blackjack(self):
        return self.value() == 21 and len(self.cards) == 2