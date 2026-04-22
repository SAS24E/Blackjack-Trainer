import json
from hand import Hand

class Player:
    """Represents a blackjack player with a hand, credits, and statistics."""
    
    def __init__(self, name):
        self.name = name.strip()  # Player's name for display purposes
        self.hand = Hand() # The player's current hand of cards
        self.credits = 1000  # Starting credits for betting
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.current_bet = 0  # Track the current bet amount for the round
        self.file_name = f"{self.name}_data.txt"  # File to save/load player data
        self.split_hands = []  # Track split hands if the player chooses to split
        self.split_bets = []  # Track bets for split hands
        
    def split_hand(self):
        """Split the player's hand into two hands if possible."""
        if len(self.hand.cards) == 2 and self.hand.cards[0].rank == self.hand.cards[1].rank:
            # Create two new hands, each with one of the split cards
            hand1 = Hand()
            hand2 = Hand()
            hand1.add_card(self.hand.cards[0])
            hand2.add_card(self.hand.cards[1])
            self.split_hands = [hand1, hand2]
            # Each hand needs a bet; deduct the second bet from credits
            self.split_bets = [self.current_bet, self.current_bet]
            if self.current_bet > self.credits:
                raise ValueError("Not enough credits to split.")
            self.subtract_credit(self.current_bet)
        else:
            raise ValueError("Cannot split: cards are not a pair.")

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
    
    def load_from_file(self, filename):
        """Load player data from a file"""
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                self.name = data.get('name', self.name)
                self.credits = data.get('credits', self.credits)
                self.wins = data.get('wins', self.wins)
                self.losses = data.get('losses', self.losses)
                self.ties = data.get('ties', self.ties)
        except FileNotFoundError:
            print(f"No save file found for {self.name}. Starting with default values.")


    def save_to_file(self, filename):
        """Save player data to a file"""
        try:
            with open(filename, 'w') as file:
                json.dump({
                    'name': self.name,
                    'credits': self.credits,
                    'wins': self.wins,
                    'losses': self.losses,
                    'ties': self.ties
                    }, file, indent=4)
        except IOError as e:
            print(f"Error saving player data: {e}")
    
    def has_split(self):
        return len(self.split_hands) > 0


