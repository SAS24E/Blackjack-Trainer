from display import Display
from hand import Hand
from deck import Deck
import time
#########################################################################################################################################################################
# BlackjackGame Class
# Attributes: deck, player_hand, dealer_hand
# Methods: update_running_count, deal_card, get_visible_value, restart_game, check_initial_blackjack, dealer_should_hit,
# dealer_play, determine_winner, player_hit, player_stand, hint_action_basic_strategy, input_action, display_graphical_hand,
# display_table, play_game
#########################################################################################################################################################################
class BlackjackGame:
        # =============================
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
            prompt = self.display.colorize("\nAction [1] Hit [2] Stand [3] Hint: ", 'yellow', bold=True)
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

        # Initial deal with animation
        import sys
        self.display.animate_deal(self.deal_card, self.player_hand, "Dealing Cards", self.player_hand, self.dealer_hand, False, self.running_count)
        self.display.animate_deal(self.deal_card, self.dealer_hand, "Dealing Cards", self.player_hand, self.dealer_hand, False, self.running_count)
        self.display.animate_deal(self.deal_card, self.player_hand, "Dealing Cards", self.player_hand, self.dealer_hand, False, self.running_count)
        self.display.animate_deal(self.deal_card, self.dealer_hand, "Initial Deal", self.player_hand, self.dealer_hand, False, self.running_count)

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

                self.display.clear_screen()
                self.display.animate_deal(self.deal_card, self.player_hand, "Player Hits", self.player_hand, self.dealer_hand, False, self.running_count)

                if self.player_hand.is_busted():
                    self.display.display_table("Round Result", player_hand=self.player_hand, dealer_hand=self.dealer_hand, reveal_dealer=True, running_count=self.running_count)
                    self.display.print_colored("Player busted! Dealer wins.", 'red', bold=True)
                    self.display.print_divider()
                    return

            elif action == '2':
                self.display.clear_screen()
                self.display.print_colored(("\nPlayer stands.", 'yellow'), 'yellow', bold=True)
                break

            elif action == '3':
                hint = self.hint_action_basic_strategy()
                self.display.print_colored(f"\nHint: You should {hint.upper()} according to basic strategy.", 'green', bold=True)

        # Dealer turn
        self.display.display_table("Dealer Reveals", player_hand=self.player_hand, dealer_hand=self.dealer_hand, reveal_dealer=True, running_count=self.running_count)

        while self.dealer_should_hit():
            self.display.animate_deal(self.deal_card, self.dealer_hand, "Dealer Hits", self.player_hand, self.dealer_hand, True, self.running_count)

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
        play_again = input(game.display.colorize("\nDo you want to play again? (y/n): ", 'orange', bold=True)).lower()
        if play_again != 'y':
            game.display.print_colored("Thanks for playing!", 'cyan', bold=True)
            break

if __name__ == "__main__":
    main()