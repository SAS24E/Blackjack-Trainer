import random
import os
import sys

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
##########################################################################################################################################################################
# Display Class
# Methods: display_graphical_hand (displays a hand using ASCII art), display_table (displays the current table state)
##########################################################################################################################################################################
class Display:
    def __init__(self):
        self.use_color = self._enable_ansi_colors()
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'cyan': '\033[36m',
            'yellow': '\033[33m',
            'green': '\033[32m',
            'red': '\033[31m',
            'magenta': '\033[35m',
        }

    def colorize(self, text, color_key, bold=False):
        if not self.use_color:
            return text

        color_code = self.colors.get(color_key, '')
        bold_code = self.colors['bold'] if bold else ''
        reset_code = self.colors['reset']
        return f"{bold_code}{color_code}{text}{reset_code}"
    
    def print_colored(self, text, color_key, bold=False):
        print(self.colorize(text, color_key, bold))


    # =============================
    # display_graphical_hand method
    # displays a hand using ASCII art
    # =============================
    def display_graphical_hand(self, hand, hide_dealer_card=False):
        card_width = 9
        card_height = 7
        card_lines = [[] for _ in range(card_height)]

        rank_symbols = {
            'ace': 'A',
            'king': 'K',
            'queen': 'Q',
            'jack': 'J',
        }

        for index, card in enumerate(hand.cards):
            if hide_dealer_card and index == 1:
                card_art = [
                    "┌───────┐",
                    "│*******│",
                    "│*******│",
                    "│*******│",
                    "│*******│",
                    "│*******│",
                    "└───────┘"
                ]
            else:
                rank_text = rank_symbols.get(card.rank, card.rank)
                card_art = [
                    "┌───────┐",
                    f"│ {rank_text:<2}    │",
                    "│       │",
                    f"│   {card.suit[0].upper()}   │",
                    "│       │",
                    f"│    {rank_text:>2} │",
                    "└───────┘"
                ]

            while len(card_art) < card_height:
                card_art.append(" " * card_width)

            for i in range(card_height):
                card_lines[i].append(card_art[i])

        for line in card_lines:
            print("  ".join(line))
        

    # =============================
    # display_table method
    # displays the current table state
    # =============================
    def display_table(self, title, player_hand, dealer_hand, reveal_dealer=False, running_count=0):
        print()
        self.print_divider()
        self.print_colored(title, 'cyan', bold=True)
        self.print_divider()

        self.print_colored(f"Running Count: {running_count}", 'cyan', bold=True)

        self.print_colored("Dealer:", 'magenta', bold=True)
        hide_card = not reveal_dealer
        self.display_graphical_hand(dealer_hand, hide_dealer_card=hide_card)
        if reveal_dealer:
            self.print_colored(f"Dealer total: {dealer_hand.value()}", 'yellow')
        else:
            self.print_colored(f"Dealer showing: {self.get_visible_value(dealer_hand, True)}", 'yellow')

        self.print_colored("Player:", 'green', bold=True)
        self.display_graphical_hand(player_hand)
        self.print_colored(f"Player total: {player_hand.value()}", 'yellow')

    def _enable_ansi_colors(self):
        # Try to enable ANSI color support on Windows terminals.
        if os.name == 'nt':
            os.system('')
        return sys.stdout.isatty()
    
    def print_divider(self):
        print(self.colorize("=" * 34, 'cyan'))  

    # =============================
    # get_visible_value method
    # returns the visible value of the dealer's hand when one card is hidden,
    # otherwise returns the total hand value
    # =============================
    def get_visible_value(self, hand, hide_dealer_card=False):
        if hide_dealer_card:
            return hand.cards[0].value()
        else:
            return hand.value()
    
#########################################################################################################################################################################
# BlackjackGame Class
# Attributes: deck, player_hand, dealer_hand
# Methods: update_running_count, deal_card, get_visible_value, restart_game, check_initial_blackjack, dealer_should_hit,
# dealer_play, determine_winner, player_hit, player_stand, hint_action_basic_strategy, input_action, display_graphical_hand,
# display_table, play_game
#########################################################################################################################################################################
class BlackjackGame:
    def __init__(self, display):
        self.display = display
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.running_count = 0

    # =============================
    # update_running_count method
    # updates the running count based on the Hi-Lo card counting system
    # =============================
    def update_running_count(self, card):
        if card.rank in ['2', '3', '4', '5', '6']:
            self.running_count += 1
        elif card.rank in ['10', 'jack', 'queen', 'king', 'ace']:
            self.running_count -= 1

    # =============================
    # deal_card method
    # deals a card from the deck to a specified Hand object
    # =============================
    def deal_card(self, hand):
        card = self.deck.deal_card()
        hand.add_card(card)
        self.update_running_count(card)

    # =============================
    # restart_game method
    # resets the game state for a new round
    # =============================
    def restart_game(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.running_count = 0

    # =============================
    # check_initial_blackjack method
    # checks if player or dealer has blackjack after the initial deal
    # =============================
    def check_initial_blackjack(self):
        player_blackjack = self.player_hand.is_blackjack()
        dealer_blackjack = self.dealer_hand.is_blackjack()

        if player_blackjack and dealer_blackjack:
            return "Both have blackjack! It's a tie!"
        if player_blackjack:
            return "Blackjack! Player wins!"
        if dealer_blackjack:
            return "Dealer has blackjack! Dealer wins."
        return None

    # =============================
    # dealer_should_hit method
    # dealer hits on 16 or lower and stands on 17 or higher
    # =============================
    def dealer_should_hit(self):
        return self.dealer_hand.value() < 17

    # =============================
    # dealer_play method
    # handles the dealer's turn
    # =============================
    def dealer_play(self):
        while self.dealer_should_hit():
            self.deal_card(self.dealer_hand)

    # =============================
    # determine_winner method
    # compares player and dealer hands and returns the game result
    # =============================
    def determine_winner(self):
        player_total = self.player_hand.value()
        dealer_total = self.dealer_hand.value()

        if player_total > 21:
            return "Dealer wins! Player busted."
        elif dealer_total > 21:
            return "Player wins! Dealer busted."
        elif player_total > dealer_total:
            return "Player wins!"
        elif dealer_total > player_total:
            return "Dealer wins!"
        else:
            return "It's a tie!"

    # =============================
    # player_hit method
    # deals one card to the player
    # =============================
    def player_hit(self):
        self.deal_card(self.player_hand)

    # =============================
    # player_stand method
    # ends player's turn and resolves dealer turn
    # =============================
    def player_stand(self):
        self.dealer_play()
        return self.determine_winner()

    # =============================
    # hint_action_basic_strategy method
    # provides a simple blackjack strategy hint
    # =============================
    def hint_action_basic_strategy(self):
        player_total = self.player_hand.value()
        dealer_card = self.display.get_visible_value(self.dealer_hand, True)
        dealer_stand_range = [2, 3, 4, 5, 6]
        dealer_bust_range = [4, 5, 6]

        if player_total >= 17:
            return "stand"
        elif player_total >= 13:
            if dealer_card in dealer_stand_range:
                return "stand"
            else:
                return "hit"
        elif player_total == 12:
            if dealer_card in dealer_bust_range:
                return "stand"
            else:
                return "hit"
        else:
            return "hit"

    # =============================
    # input_action method
    # prompts the player for an action and validates input
    # =============================
    def input_action(self):
        actions = {
            '1': 'hit',
            '2': 'stand',
            '3': 'hint'
        }

        while True:
            prompt = self.display.colorize("Action [1] Hit [2] Stand [3] Hint: ", 'yellow', bold=True)
            choice = input(prompt).strip()
            if choice in actions:
                return choice
            else:
                self.display.print_colored("Invalid input. Please enter 1, 2, or 3.", 'red', bold=True)

    # =============================
    # play_game method
    # orchestrates the flow of one round of blackjack
    # =============================
    def play_game(self):
        self.restart_game()

        # Initial deal
        self.deal_card(self.player_hand)
        self.deal_card(self.dealer_hand)
        self.deal_card(self.player_hand)
        self.deal_card(self.dealer_hand)

        self.display.display_table("Initial Deal", player_hand=self.player_hand, dealer_hand=self.dealer_hand, reveal_dealer=False, running_count=self.running_count)

        blackjack_result = self.check_initial_blackjack()
        if blackjack_result:
            self.display.display_table("Round Result", player_hand=self.player_hand, dealer_hand=self.dealer_hand, reveal_dealer=True, running_count=self.running_count)
            self.display.print_colored("", 'green', bold=True)
            self.display.print_divider()  
            self.display.print_colored(blackjack_result, 'green', bold=True)
            self.display.print_divider()
            return

        # Player turn
        while True:
            action = self.input_action()

            if action == '1':
                self.player_hit()
                self.display.display_table("Player Hits", player_hand=self.player_hand, dealer_hand=self.dealer_hand, reveal_dealer=False, running_count=self.running_count)

                if self.player_hand.is_busted():
                    self.display.display_table("Round Result", player_hand=self.player_hand, dealer_hand=self.dealer_hand, reveal_dealer=True, running_count=self.running_count)
                    self.display.print_colored("Player busted! Dealer wins.", 'red', bold=True)
                    self.display.print_divider()
                    return

            elif action == '2':
                self.display.print_colored("\n" + self.display.colorize("Player stands.", 'yellow'), 'yellow', bold=True)
                break

            elif action == '3':
                hint = self.hint_action_basic_strategy()
                self.display.print_colored("\n" + self.display.colorize(f"Hint: You should {hint.upper()} according to basic strategy.", 'yellow', bold=True), 'yellow', bold=True)

        # Dealer turn
        self.display.display_table("Dealer Reveals", player_hand=self.player_hand, dealer_hand=self.dealer_hand, reveal_dealer=True, running_count=self.running_count)

        while self.dealer_should_hit():
            self.deal_card(self.dealer_hand)
            self.display.display_table("Dealer Hits", player_hand=self.player_hand, dealer_hand=self.dealer_hand, reveal_dealer=True, running_count=self.running_count)

        self.display.display_table("Final Hands", player_hand=self.player_hand, dealer_hand=self.dealer_hand, reveal_dealer=True, running_count=self.running_count)

        # Result
        result = self.determine_winner()
        result_color = 'green' if 'Player wins' in result else 'red' if 'Dealer wins' in result else 'yellow'
        self.display.print_colored("", 'green', bold=True)
        self.display.print_divider()
        self.display.print_colored(result, result_color, bold=True)
        self.display.print_divider()


# =============================
# TESTING BLOCK For main program.
# =============================
def main():
    display = Display()
    game = BlackjackGame(display)
    while True:
        game.play_game()
        play_again = input(game.display.colorize("Do you want to play again? (y/n): ", 'yellow', bold=True)).lower()
        if play_again != 'y':
            game.display.print_colored("Thanks for playing!", 'cyan', bold=True)
            break

if __name__ == "__main__":
    main()