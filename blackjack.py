from deck import Deck
from hand import Hand
from basicstrategy import BasicStrategy


class BlackjackGame:
    """Core blackjack game logic."""

    # === Constants ===
    LOW_COUNT_CARDS = {"2", "3", "4", "5", "6"}
    HIGH_COUNT_CARDS = {"10", "jack", "queen", "king", "ace"}

    # === Initialization ===
    def __init__(self, ui, player):
        self.ui = ui 
        self.deck = Deck() 
        self.player = player 
        self.running_count = 0
        self.reshuffle_threshold = 15
        self.current_bet = 0
        self.dealer_hole_card_revealed = False
        self.basic_strategy = BasicStrategy(self)

    # === Deck & Card Counting ===
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

    def reshuffle_if_needed(self):
        """Reshuffle between rounds when the deck is running low."""
        if len(self.deck.cards) < self.reshuffle_threshold:
            self.deck = Deck()
            self.running_count = 0

    def dealer_upcard_value(self):
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

    # === Game State ===
    def reset_hands(self):
        """Prepare a fresh round while keeping the current shoe."""
        self.player.hand = Hand()
        self.player.split_hands = []
        self.player.split_bets = []
        self.dealer_hand = Hand()
        self.dealer_hole_card_revealed = False

    def get_table_state(self, title, reveal_dealer=False):
        """Return the current state needed by the UI layer."""
        return {
            "title": title,
            "player_hand": self.player.hand,
            "dealer_hand": self.dealer_hand,
            "reveal_dealer": reveal_dealer,
            "running_count": self.running_count,
            "dealer_upcard_value": self.dealer_upcard_value(),
            "player_credits": self.player.credits,
        }

    def start_round(self):
        """Prepare the game state for a new round."""
        self.reshuffle_if_needed()
        self.reset_hands()
        self.current_bet = self.ui.input_bet(self.player.credits)
        self.player.place_bet(self.current_bet)

    # === Round Rules ===
    def check_initial_blackjack(self):
        """Return the opening-round result when a blackjack is present."""
        player_blackjack = self.player.hand.is_blackjack()
        dealer_blackjack = self.dealer_hand.is_blackjack()

        if player_blackjack and dealer_blackjack:
            self.player.push_bet(self.player.current_bet)
            return "Both have blackjack! It's a tie(Push)!"
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

    def compare_hands(self):
        """Compare player and dealer hands without updating credits."""
        player_total = self.player.hand.value()
        dealer_total = self.dealer_hand.value()

        if player_total > 21:
            return "Dealer wins! Player busted."
        if dealer_total > 21:
            return "Player wins! Dealer busted."
        if player_total > dealer_total:
            return "Player wins!"
        if dealer_total > player_total:
            return "Dealer wins!"
        return "It's a tie(Push)!"

    def determine_winner(self):
        """Compare hands, update credits, and return the round result."""
        result = self.compare_hands()
        self.update_hand_result(result, self.player.current_bet)
        self.ui.render_credits(self.player.credits)
        return result

    def can_double_down(self):
        """Return True when the player can still legally double down."""
        return len(self.player.hand.cards) == 2 and (self.player.current_bet * 2) <= self.player.credits

    def can_split(self):
        """Return True when the player can legally split the current hand."""
        return (
            not self.player.has_split()
            and len(self.player.hand.cards) == 2
            and self.player.hand.cards[0].rank == self.player.hand.cards[1].rank
            and (self.player.current_bet * 2) <= self.player.credits
        )

    # === Round Flow ===
    def initial_deal(self):
        """Deal the opening four cards and return any blackjack result."""
        self.ui.animate_deal(self.deal_card, self.player.hand, lambda: self.get_table_state("Dealing Cards"))
        self.ui.animate_deal(self.deal_card, self.dealer_hand, lambda: self.get_table_state("Dealing Cards"))
        self.ui.animate_deal(self.deal_card, self.player.hand, lambda: self.get_table_state("Dealing Cards"))
        self.ui.animate_deal(
            lambda hand: self.deal_card(hand, count_card=False),
            self.dealer_hand,
            lambda: self.get_table_state("Initial Deal"),
        )
        return self.check_initial_blackjack()

    def handle_hit_action(self):
        """Resolve a hit action. Return True/False when the turn must end, else None."""
        self.ui.clear_screen()
        self.ui.animate_deal(self.deal_card, self.player.hand, lambda: self.get_table_state("Player Hits"))

        if self.player.hand.is_busted():
            if self.player.has_split():
                self.ui.print_colored("\nHand busted.", "red", bold=True)
                return False

            self.player.lost_bet(self.player.current_bet)
            self.count_dealer_hidden_card()
            self.show_result("Round Result", "Player busted! Dealer wins.", "red")
            return True

        if self.player.hand.value() == 21:
            self.ui.print_colored("\nPlayer reached 21 and stands automatically.", "yellow", bold=True)
            return False

        return None

    def handle_stand_action(self):
        """Resolve a stand action."""
        self.ui.print_colored("\nPlayer stands.", "yellow", bold=True)
        return False

    def handle_double_action(self):
        """Resolve a double-down action."""
        self.player.place_bet(self.player.current_bet * 2)
        self.ui.clear_screen()
        self.ui.animate_deal(
            self.deal_card,
            self.player.hand,
            lambda: self.get_table_state("Player Doubles and Stands"),
        )

        if self.player.hand.is_busted():
            if self.player.has_split():
                self.ui.print_colored("\nHand busted.", "red", bold=True)
                return False

            self.player.lost_bet(self.player.current_bet)
            self.count_dealer_hidden_card()
            self.show_result("Round Result", "Player busted! Dealer wins.", "red")
            return True

        if self.player.hand.value() == 21:
            self.ui.print_colored("\nPlayer doubled to 21 and stands automatically.", "yellow", bold=True)

        return False

    def handle_split_action(self):
        """Resolve a split action."""
        self.handle_split_hand()
        return False

    def handle_hint_action(self):
        """Show a basic strategy hint."""
        hint = self.basic_strategy.hint_action_basic_strategy()
        self.ui.print_colored(
            f"\nHint: You should {hint.upper()} according to basic strategy.",
            "green",
            bold=True,
        )

    def handle_player_turn(self):
        """Run the player's turn. Return True if the round ends here."""
        while True:
            hand_length = len(self.player.hand.cards)
            action = self.ui.input_action(hand_length, self.can_double_down(), self.can_split())

            if action == "hit":
                result = self.handle_hit_action()
                if result is not None:
                    return result
            elif action == "stand":
                return self.handle_stand_action()
            elif action == "double" and self.can_double_down():
                return self.handle_double_action()
            elif action == "split" and self.can_split():
                return self.handle_split_action()
            else:
                self.handle_hint_action()

    def handle_dealer_turn(self):
        """Reveal the dealer hand and play out dealer hits."""
        self.count_dealer_hidden_card()
        self.ui.render_table(**self.get_table_state("Dealer Reveals", reveal_dealer=True))

        while self.dealer_should_hit():
            self.ui.animate_deal(
                self.deal_card,
                self.dealer_hand,
                lambda: self.get_table_state("Dealer Hits", reveal_dealer=True),
            )

    def handle_split_hand(self):
        """Handle splitting the player's hand when two initial cards are the same rank."""
        self.player.split_hand()

        for i, hand in enumerate(self.player.split_hands):
            self.player.hand = hand
            self.ui.clear_screen()
            self.ui.animate_deal(
                self.deal_card,
                self.player.hand,
                lambda i=i: self.get_table_state(f"Dealing card to Hand {i + 1}"),
            )

        for i, hand in enumerate(self.player.split_hands):
            self.player.hand = hand
            self.player.current_bet = self.player.split_bets[i]
            self.ui.clear_screen()
            self.ui.render_table(
                **self.get_table_state(f">>> PLAYING HAND {i + 1} of {len(self.player.split_hands)} <<<")
            )
            self.ui.print_colored(f"\n=== HAND {i + 1} ===", "cyan", bold=True)
            self.handle_player_turn()
            self.player.split_bets[i] = self.player.current_bet

        self.player.hand = self.player.split_hands[0]

    # === Result Display ===
    def get_result_color(self, result):
        """Return display color based on game result."""
        if "Player wins" in result:
            return "green"
        if "Dealer wins" in result or "busted" in result:
            return "red"
        return "yellow"

    def display_result_section(self, result_text, color):
        """Display a formatted result section with dividers."""
        self.ui.print_colored("", "green", bold=True)
        self.ui.print_divider()
        self.ui.print_colored(result_text, color, bold=True)
        self.ui.print_divider()

    def show_result(self, title, message, color):
        """Render a final round state and its result message."""
        self.ui.render_table(**self.get_table_state(title, reveal_dealer=True))
        self.display_result_section(message, color)

    def show_final_result(self):
        """Display the final hands and winner."""
        if self.player.has_split():
            self.show_split_hand_results()
        else:
            self.show_single_hand_result()

    def show_split_hand_results(self):
        """Display results for each split hand."""
        for i, hand in enumerate(self.player.split_hands):
            self.player.hand = hand
            hand_bet = self.player.split_bets[i]
            self.ui.clear_screen()
            self.ui.render_table(
                **self.get_table_state(f">>> FINAL HAND {i + 1} of {len(self.player.split_hands)} <<<", reveal_dealer=True)
            )
            result = self.compare_hands()
            self.update_hand_result(result, hand_bet)

            self.ui.render_credits(self.player.credits)
            result_color = self.get_result_color(result)
            self.display_result_section(f"HAND {i + 1}: {result}", result_color)

        self.player.hand = self.player.split_hands[0]

    def show_single_hand_result(self):
        """Display result for a single non-split hand."""
        self.ui.render_table(**self.get_table_state("Final Hands", reveal_dealer=True))
        result = self.determine_winner()
        result_color = self.get_result_color(result)
        self.display_result_section(result, result_color)

    def update_hand_result(self, result, hand_bet):
        """Update credits and stats based on a hand result."""
        if "Player wins" in result:
            self.player.won_bet(hand_bet)
        elif "Dealer wins" in result:
            self.player.lost_bet(hand_bet)
        else:
            self.player.push_bet(hand_bet)

    # === Game Loop ===
    def play_game(self):
        """Play one round of blackjack."""
        self.start_round()

        blackjack_result = self.initial_deal()
        if blackjack_result:
            self.count_dealer_hidden_card()
            self.show_result("Round Result", blackjack_result, self.get_result_color(blackjack_result))
            return

        if self.handle_player_turn():
            return

        self.handle_dealer_turn()
        self.show_final_result()
