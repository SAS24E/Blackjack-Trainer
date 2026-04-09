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

# Deck class
    
# Hand Class
# 
#########################################################################################################################################################################
# BlackjackGame Class
# Attributes: deck, player_hand, dealer_hand
# Methods: create_deck, print_deck, deal_card, calculate_hand_value, display_hand, get_visible_value, restart_game, is_blackjack, is_busted, dealer_should_hit, dealer_play, determine_winner, player_hit, player_stand, input_action, play_game
#########################################################################################################################################################################
class BlackjackGame:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.use_color = self._enable_ansi_colors()
        self.running_count = 0  

        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'cyan': '\033[36m',
            'yellow': '\033[33m',
            'green': '\033[32m',
            'red': '\033[31m',
            'magenta': '\033[35m',
        }

    def _enable_ansi_colors(self):
        # Try to enable ANSI color support on Windows terminals.
        if os.name == 'nt': # Windows nt is the OS name for Windows , linux is posix however we dont need to check for linux since ANSI colors are widely supported in modern terminals on Linux and macOS by default.
            os.system('') 
        return sys.stdout.isatty()

    def colorize(self, text, color_key, bold=False):
        if not self.use_color:
            return text

        color_code = self.colors.get(color_key, '')
        bold_code = self.colors['bold'] if bold else ''
        reset_code = self.colors['reset']
        return f"{bold_code}{color_code}{text}{reset_code}"

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
        random.shuffle(deck)  # shuffle the deck to randomize the order of the cards
        return deck
    # =============================
    # update_running_count method
    # This method updates the running count for card counting based on the value of the card that
    # is dealt. It uses the Hi-Lo counting system where cards 2-6 increase the count by 1, cards 10-Ace decrease the count by 1, and cards 7-9 do not affect the count.
    # =============================
    def update_running_count(self, card):
        # Update the running count based on the value of the card.
        if card.rank in ['2', '3', '4', '5', '6']:
            self.running_count += 1
        elif card.rank in ['10', 'jack', 'queen', 'king', 'ace']:
            self.running_count -= 1

    # =============================
    # deal_card method
    # Deals a card from the deck to a specified hand (either player or dealer).
    # It removes the top card from the deck and adds it to the specified hand.
    # =============================
    def deal_card(self, hand):
        card = self.deck.pop()  # remove the top card from the deck
        hand.append(card)  # add the card to the specified hand
        self.update_running_count(card)  # Update the running count whenever a card is dealt

    # =============================
    # calculate_hand_value method
    # Takes a hand (either player or dealer) and calculates the total value of the hand according to blackjack rules.
    # =============================
    def calculate_hand_value(self, hand):
        total = 0
        aces = 0
        for card in hand:
            total += card.value()
            if card.rank == 'ace':
                aces += 1
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total


    # =============================
    # get_visible_value method
    # This method returns the value of the visible card in the dealer's hand if the dealer's second card is hidden, otherwise it returns the total value of the hand.
    # =============================
    def get_visible_value(self, hand, hide_dealer_card=False):
        if hide_dealer_card:
            return hand[0].value()
        else:
            return self.calculate_hand_value(hand)

    # =============================
    # restart_game method
    # This method resets the game state by creating a new shuffled deck and clearing both the player's and dealer's hands.
    #  This allows the game to be restarted without needing to create a new instance of the BlackjackGame class.
    # =============================
    def restart_game(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
        self.running_count = 0  # Reset the running count when the game is restarted

    # =============================
    # is_blackjack method
    # returns True if the hand is a blackjack (total value of 21 with only two cards), otherwise returns False.
    # =============================
    def is_blackjack(self, hand):
        return self.calculate_hand_value(hand) == 21 and len(hand) == 2
    # =============================
    # check_initial_blackjack method
    # This method checks if either the player or the dealer has a blackjack (a hand value of 21 with only two cards) at the start of the game.
    # It returns a string indicating the outcome if there is a blackjack (e.g., "Blackjack! Player wins!", "Dealer has blackjack! Dealer wins.", "Both have blackjack! It's a tie!"), or None if there is no blackjack.
    # =============================
    def check_initial_blackjack(self):
        player_blackjack = self.is_blackjack(self.player_hand)
        dealer_blackjack = self.is_blackjack(self.dealer_hand)

        if player_blackjack and dealer_blackjack:
            return "Both have blackjack! It's a tie!"
        if player_blackjack:
            return "Blackjack! Player wins!"
        if dealer_blackjack:
            return "Dealer has blackjack! Dealer wins."
        return None

    # =============================
    # is_busted method
    # returns True if the total value of the hand exceeds 21, indicating that the player or
    # dealer has busted, otherwise returns False.
    # =============================
    def is_busted(self, hand):
        return self.calculate_hand_value(hand) > 21

    # =============================
    # dealer_should_hit method
    # This method determines whether the dealer should hit (take another card) based on the total value
    # dealer stands on 17 or higher and hits on 16 or lower. It returns True if the dealer should hit, otherwise it returns False.
    # =============================
    def dealer_should_hit(self):
        return self.calculate_hand_value(self.dealer_hand) < 17

    # =============================
    # dealer_play method
    # This method handles the dealer's turn. It continues to deal cards to the dealer's hand as long as the dealer should hit according to the dealer_should_hit method.
    # Once the dealer stands (when the dealer's hand value is 17 or higher), the method ends and the game can proceed to determine the winner.
    # =============================
    def dealer_play(self):
        while self.dealer_should_hit():
            self.deal_card(self.dealer_hand)

    # =============================
    # determine_winner method
    # This method compares the total value of the player's hand and the dealer's hand to determine the
    # winner of the game. It checks for various conditions such as if the player has busted, if the dealer has busted, or if one hand has a higher value than the other.
    # It returns a string indicating the outcome of the game (e.g., "Player wins!", "Dealer wins!", "It's a tie!").
    # =============================
    def determine_winner(self):
        player_total = self.calculate_hand_value(self.player_hand)
        dealer_total = self.calculate_hand_value(self.dealer_hand)
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
    # This method allows the player to take another card (hit). It calls the deal_card method
    # to add a card to the player's hand. After the player hits, the game can check if the player has busted or if they want to hit again.
    # =============================
    def player_hit(self):
        self.deal_card(self.player_hand)

    # =============================
    # player_stand method
    # This method allows the player to end their turn (stand).
    # It calls the dealer_play method to let the dealer take their turn,
    # and then it calls the determine_winner method to compare the player's hand and the dealer's hand and determine the outcome of the game.
    # =============================
    def player_stand(self):
        self.dealer_play()
        return self.determine_winner()
    # =============================
    # hint_action_basic_strategy method
    # This method provides a hint to the player based on basic blackjack strategy. It evaluates the
    # player's hand value and the dealer's visible card to suggest whether the player should hit or stand according to standard blackjack strategy guidelines.
    # =============================
    def hint_action_basic_strategy(self):
        player_total = self.calculate_hand_value(self.player_hand)
        dealer_card = self.get_visible_value(self.dealer_hand, True)
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
        else: # player_total <= 11
            return "hit"



    # =============================
    # input_action method
    # This method prompts the player to choose an action (hit, stand, double down, split) and validates the input to ensure it is a valid action.
    # It continues to prompt the player until a valid action is entered and then returns the chosen action for further processing in the game logic
    # =============================
    def input_action(self):
        actions = {
            '1': 'hit',
            '2': 'stand',
            '3': 'hint'
        }
        while True:
            prompt = self.colorize("Action [1] Hit [2] Stand [3] Hint: ", 'yellow', bold=True)
            choice = input(prompt).strip()
            if choice in actions:
                return choice
            else:
                print(self.colorize("Invalid choice. Please enter 1, 2, or 3.", 'red', bold=True))

    def display_graphical_hand(self, hand, hide_dealer_card=False):
        # Using ASCII art to display the hand of cards in a visually appealing way.
        card_width = 9  # Fixed width for each card
        card_height = 7  # Fixed height for each card
        card_lines = [[] for _ in range(card_height)]  # Create lines for the card display

        rank_symbols = {
            'ace': 'A',
            'king': 'K',
            'queen': 'Q',
            'jack': 'J',
        }

        for index, card in enumerate(hand):
            if hide_dealer_card and index == 1:  # Hide the dealer's second card
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

            # Ensure card_art has exactly card_height lines
            while len(card_art) < card_height:
                card_art.append(" " * card_width)

            for i in range(card_height):
                card_lines[i].append(card_art[i])

        # Print all lines with uniform spacing between cards
        for line in card_lines:
            print("  ".join(line))  # Add two spaces between cards for better alignment
            
    # =============================
    # display_table method
    # This method displays the current state of the game table, including the player's hand and the dealer's hand.
    # It takes a title to indicate the current phase of the game and a boolean flag to determine whether to reveal the dealer's hidden card.
    # The method uses ASCII art to visually represent the cards in both hands and shows the total value of the player's hand and either the visible card or total value of the dealer's hand based on the reveal_dealer flag.
    # =============================       
    def display_table(self, title, reveal_dealer=False):
        divider = self.colorize("=" * 34, 'cyan')
        print("\n" + divider)
        print(self.colorize(title, 'cyan', bold=True))
        print(divider)
        
        print(self.colorize(f"Running Count: {self.running_count}", 'cyan', bold=True))  # Display the running count for card counting purposes
        
        print(self.colorize("Dealer:", 'magenta', bold=True))
        hide_card = not reveal_dealer  # Explicit variable for clarity
        self.display_graphical_hand(self.dealer_hand, hide_dealer_card=hide_card)
        if reveal_dealer:
            print(self.colorize(f"Dealer total: {self.calculate_hand_value(self.dealer_hand)}", 'yellow'))
        else:
            print(self.colorize(f"Dealer showing: {self.get_visible_value(self.dealer_hand, True)}", 'yellow'))

        print("\n" + self.colorize("Player:", 'green', bold=True))
        self.display_graphical_hand(self.player_hand)
        print(self.colorize(f"Player total: {self.calculate_hand_value(self.player_hand)}", 'yellow'))

    # =============================
    # play_game method
    # This method orchestrates the flow of the game. It starts by restarting the game to reset the game state,
    #  then it handles the initial deal of cards to both the player and the dealer.
    # It displays the player's hand and the dealer's visible card,
    # and then it enters a loop to allow the player to choose actions (hit, stand, double down, split) until the player stands or busts.
    # After the player's turn, it handles the dealer's turn and then determines the winner of the game based on the final hands of both the player and the dealer.
    # The method also includes print statements to display the game state and results to the player throughout the game.
    # =============================
    def play_game(self):
        self.restart_game()

        # Initial deal
        self.deal_card(self.player_hand)
        self.deal_card(self.dealer_hand)
        self.deal_card(self.player_hand)
        self.deal_card(self.dealer_hand)
        # Display the initial hands with the dealer's second card hidden
        self.display_table("Initial Deal", reveal_dealer=False)

        # Blackjack check / Auto-resolve if either side has a natural blackjack on the initial deal.
        blackjack_result = self.check_initial_blackjack()
        if blackjack_result:
            self.display_table("Round Result", reveal_dealer=True)
            divider = self.colorize("=" * 34, 'cyan')
            print("\n" + divider)
            print(self.colorize(blackjack_result, 'green', bold=True))
            print(divider)
            return

        # Player turn 
        while True: # Loop to allow the player to choose actions until they stand or bust.
            action = self.input_action() # Prompt the player to choose an action (hit, stand, double down, split) and validate the input.

            if action == '1':  # hit
                self.player_hit()
                self.display_table("Player Hits", reveal_dealer=False)

                if self.is_busted(self.player_hand): # Check if the player has busted after hitting. If the player's hand value exceeds 21, they have busted and the game should end with the dealer winning.
                    self.display_table("Round Result", reveal_dealer=True) 
                    print(self.colorize("Player busted! Dealer wins.", 'red', bold=True)) #
                    return

            elif action == '2':  # stand 
                print("\n" + self.colorize("Player stands.", 'yellow'))
                break # Exit the loop to end the player's turn and proceed to the dealer's turn.
            elif action == '3':
                # hint button for basic strategy
                hint = self.hint_action_basic_strategy()
                print("\n" + self.colorize(f"Hint: You should {hint.upper()} according to basic strategy.", 'yellow', bold=True))

        # Dealer turn
        self.display_table("Dealer Reveals", reveal_dealer=True)

        while self.dealer_should_hit(): # Loop to allow the dealer to take their turn according to standard dealer rules (dealer stands on 17 or higher and hits on 16 or lower).
            self.deal_card(self.dealer_hand) # Deal a card to the dealer's hand if the dealer should hit (if the dealer's hand value is less than 17).
            self.display_table("Dealer Hits", reveal_dealer=True) # Display the game state after the dealer takes a card, showing the dealer's hand with all cards revealed.

        self.display_table("Final Hands", reveal_dealer=True) # Display the final hands of both the player and the dealer after the dealer has completed their turn, showing all cards revealed and the total values of both hands.

        # Result
        result = self.determine_winner() # Determine the winner of the game by comparing the player's hand and the dealer's hand according to blackjack rules (e.g., if the player has busted, if the dealer has busted, or if one hand has a higher value than the other).
        divider = self.colorize("=" * 34, 'cyan') 
        result_color = 'green' if 'Player wins' in result else 'red' if 'Dealer wins' in result else 'yellow' 
        print("\n" + divider)
        print(self.colorize(result, result_color, bold=True))
        print(divider)


# =============================
# TESTING BLOCK For main program.
# =============================
if __name__ == "__main__":
    game = BlackjackGame()  # define a game instance
    while True:
        game.play_game()  # start the game
        play_again = input(game.colorize("Do you want to play again? (y/n): ", 'yellow', bold=True)).lower() # Prompt the player to decide if they want to play another round after the current game ends. The input is converted to lowercase to allow for case-insensitive input (e.g., 'Y' or 'y' will both be accepted as yes).
        if play_again != 'y':
            print(game.colorize("Thanks for playing!", 'cyan', bold=True))
            break
