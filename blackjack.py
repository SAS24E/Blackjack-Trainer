from deck import Deck
from hand import Hand


class BlackjackGame:
    """Core blackjack game logic."""

    LOW_COUNT_CARDS = {"2", "3", "4", "5", "6"} 
    HIGH_COUNT_CARDS = {"10", "jack", "queen", "king", "ace"} 

    # Setup
    def __init__(self, display, player):
        self.display = display
        self.deck = Deck()
        self.player = player
        self.running_count = 0
        self.reshuffle_threshold = 15
        self.current_bet = 0
        self.dealer_hole_card_revealed = False

    # Deck and state helpers
    def update_running_count(self, card):
        """Update the running count using the Hi-Lo system."""
        if card.rank in self.LOW_COUNT_CARDS:
            self.running_count += 1
        elif card.rank in self.HIGH_COUNT_CARDS:
            self.running_count -= 1

    def deal_card(self, hand, count_card=True):
        """Deal one card to the given hand."""
        if not self.deck.cards:
            raise RuntimeError("The deck ran out of cards during the round.")

        card = self.deck.deal_card()
        hand.add_card(card)
        if count_card:
            self.update_running_count(card)

    def reset_hands(self):
        """Prepare a fresh round while keeping the current shoe."""
        self.player.hand = Hand()
        self.dealer_hand = Hand()
        self.dealer_hole_card_revealed = False

    def reshuffle_if_needed(self):
        """Reshuffle between rounds when the deck is running low."""
        if len(self.deck.cards) < self.reshuffle_threshold:
            self.deck = Deck()
            self.running_count = 0

    def get_dealer_visible_value(self):
        """Return the dealer's upcard value."""
        if not self.dealer_hand.cards:
            return 0
        return self.dealer_hand.cards[0].value()

    def count_dealer_hidden_card(self):
        """Add the dealer's hidden card to the count the first time it is revealed."""
        if self.dealer_hole_card_revealed or len(self.dealer_hand.cards) < 2:
            return
        self.update_running_count(self.dealer_hand.cards[1])
        self.dealer_hole_card_revealed = True

    def get_table_state(self, title, reveal_dealer=False):
        """Return the current state needed by the display layer."""
        return {
            "title": title,
            "player_hand": self.player.hand,
            "dealer_hand": self.dealer_hand,
            "reveal_dealer": reveal_dealer,
            "running_count": self.running_count,
            "dealer_visible_value": self.get_dealer_visible_value(),
            "player_credits": self.player.credits,
        }

    # Round rules
    def start_round(self):
        """Prepare the game state for a new round."""
        self.reshuffle_if_needed()
        self.reset_hands()
        self.current_bet = self.display.input_bet(self.player.credits)
        self.player.place_bet(self.current_bet)

    def check_initial_blackjack(self):
        """Return the opening-round result when a blackjack is present."""
        player_blackjack = self.player.hand.is_blackjack()
        dealer_blackjack = self.dealer_hand.is_blackjack()

        if player_blackjack and dealer_blackjack:
            self.player.push_bet(self.player.current_bet)
            return "Both have blackjack! It's a tie!"
        if player_blackjack:
            self.player.won_bet(self.player.current_bet * 1.5)
            return "Blackjack! Player wins!"
        if dealer_blackjack:
            self.player.lost_bet(self.player.current_bet)
            return "Dealer has blackjack! Dealer wins."
        return None

    def dealer_should_hit(self):
        """Dealer hits on 16 or lower and stands on 17 or higher."""
        return self.dealer_hand.value() < 17

    def determine_winner(self):
        """Compare hands and return the round result."""
        player_total = self.player.hand.value()
        dealer_total = self.dealer_hand.value()

        if player_total > 21:
            self.player.lost_bet(self.player.current_bet)
            return "Dealer wins! Player busted."
        if dealer_total > 21:
            self.player.won_bet(self.player.current_bet)
            return "Player wins! Dealer busted."
        if player_total > dealer_total:
            self.player.won_bet(self.player.current_bet)
            return "Player wins!"
        if dealer_total > player_total:
            self.player.lost_bet(self.player.current_bet)
            return "Dealer wins!"
        self.player.push_bet(self.player.current_bet)
        return "It's a tie!"

    def hint_action_basic_strategy(self):
        """Return a simple hit-or-stand basic-strategy hint."""
        # need to add double down basic strategy hints here as well.  ## Remove comment when added
        player_total = self.player.hand.value()
        dealer_card = self.get_dealer_visible_value()

        if player_total >= 17:
            return "stand"
        if player_total >= 13:
            return "stand" if dealer_card in {2, 3, 4, 5, 6} else "hit"
        if player_total == 12:
            return "stand" if dealer_card in {4, 5, 6} else "hit"
        return "hit"
    

    # Round flow
    def show_result(self, title, message, color):
        """Render a final round state and its result message."""
        self.display.display_table(**self.get_table_state(title, reveal_dealer=True))
        self.display.print_colored("", "green", bold=True)
        self.display.print_divider()
        self.display.print_colored(message, color, bold=True)
        self.display.print_divider()

    def initial_deal(self):
        """Deal the opening four cards and return any blackjack result."""
        self.display.animate_deal(self.deal_card, self.player.hand, lambda: self.get_table_state("Dealing Cards"))
        self.display.animate_deal(self.deal_card, self.dealer_hand, lambda: self.get_table_state("Dealing Cards"))
        self.display.animate_deal(self.deal_card, self.player.hand, lambda: self.get_table_state("Dealing Cards"))
        self.display.animate_deal(
            lambda hand: self.deal_card(hand, count_card=False),
            self.dealer_hand,
            lambda: self.get_table_state("Initial Deal"),
        )
        return self.check_initial_blackjack()

    def handle_player_turn(self):
        """Run the player's turn. Return True if the round ends here."""
        while True:
            action = self.display.input_action()

            if action == "hit": # Thanks to input_action we are able to use the string "hit" instead of a numeric choice here.
                self.display.clear_screen()
                self.display.animate_deal(self.deal_card, self.player.hand, lambda: self.get_table_state("Player Hits"))

                if self.player.hand.is_busted():
                    self.player.lost_bet(self.player.current_bet)
                    self.show_result("Round Result", "Player busted! Dealer wins.", "red")
                    return True
            elif action == "stand":
                self.display.print_colored("\nPlayer stands.", "yellow", bold=True)
                return False
            elif action == "double" and self.player.current_bet <= self.player.credits and len(self.player.hand.cards) == 2: # Handle double means we need to double the current bet and close out.
                self.player.place_bet(self.player.current_bet * 2)
                self.display.clear_screen()
                self.display.animate_deal(self.deal_card, self.player.hand, lambda: self.get_table_state("Player Doubles and Stands"))
                if self.player.hand.is_busted():
                    self.player.lost_bet(self.player.current_bet)
                    self.show_result("Round Result", "Player busted! Dealer wins.", "red")
                    return True
                return False
            else:
                hint = self.hint_action_basic_strategy()
                self.display.print_colored(
                    f"\nHint: You should {hint.upper()} according to basic strategy.",
                    "green",
                    bold=True,
                )

    def handle_dealer_turn(self):
        """Reveal the dealer hand and play out dealer hits."""
        self.count_dealer_hidden_card()
        self.display.display_table(**self.get_table_state("Dealer Reveals", reveal_dealer=True))

        while self.dealer_should_hit():
            self.display.animate_deal(
                self.deal_card,
                self.dealer_hand,
                lambda: self.get_table_state("Dealer Hits", reveal_dealer=True),
            )

    def show_final_result(self):
        """Display the final hands and winner."""
        self.display.display_table(**self.get_table_state("Final Hands", reveal_dealer=True))
        result = self.determine_winner()

        if "Player wins" in result:
            result_color = "green"
        elif "Dealer wins" in result:
            result_color = "red"
        else:
            result_color = "yellow"

        self.display.print_colored("", "green", bold=True)
        self.display.print_divider()
        self.display.print_colored(result, result_color, bold=True)
        self.display.print_divider()

    def play_game(self):
        """Play one round of blackjack."""
        self.start_round()

        blackjack_result = self.initial_deal()
        if blackjack_result:
            self.count_dealer_hidden_card()
            self.show_result("Round Result", blackjack_result, "green")
            return

        if self.handle_player_turn():
            return

        self.handle_dealer_turn()
        self.show_final_result()
