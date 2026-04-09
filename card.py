#########################################################################################################################################################################
# Card Class
# Attributes: rank, suit
# Methods: value (returns the value of the card for blackjack)
#########################################################################################################################################################################
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank.capitalize()} of {self.suit.capitalize()}"
        
    # =============================
    # Card Value Method
    # returns the value of the card for blackjack
    # =============================
    def value(self):
        if self.rank in ['jack', 'queen', 'king']:
            return 10
        elif self.rank == 'ace':
            return 11
        else:
            return int(self.rank)