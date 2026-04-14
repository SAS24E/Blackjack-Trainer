
from hand import Hand

class Player:
    def __init__(self, name):
        self.name = name # Player's name for display purposes
        self.hand = Hand() # The player's current hand of cards
        self.credits = 1000  # Starting credits for betting
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.current_bet = 0  # Track the current bet amount for the round

    def add_credit(self, amount):
        """Add credits to the player's balance."""
        self.credits += amount

    def subtract_credit(self, amount):
        """Subtract credits from the player's balance."""
        if amount > self.credits:
            raise ValueError("Insufficient credits.")
        self.credits -= amount


    def won_bet(self, amount):
        """Handle winning a bet."""
        self.add_credit(amount)
        self.wins += 1

    def lost_bet(self, amount):
        """Handle losing a bet."""
        self.subtract_credit(amount)
        self.losses += 1

    def push_bet(self, amount):
        """Handle a tie (push) in a bet."""
        self.ties += 1

    def place_bet(self, amount):
        """Place a bet for the current round."""
        if amount > self.credits:
            raise ValueError("Bet amount exceeds available credits.")
        if amount <= 0:
            raise ValueError("Bet amount must be greater than zero.")
        self.current_bet = amount
        return self.current_bet
    
        
