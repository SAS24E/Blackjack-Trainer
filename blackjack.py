from deck import Deck
from hand import Hand


class BlackjackGame:
    """Core blackjack game logic."""

    # === Constants ===
    LOW_COUNT_CARDS = {"2", "3", "4", "5", "6"}
    HIGH_COUNT_CARDS = {"10", "jack", "queen", "king", "ace"}

    # === Initialization ===
    def __init__(self, display, player):
        self.display = display
        self.deck = Deck()
        self.player = player
        self.running_count = 0
        self.reshuffle_threshold = 15
        self.current_bet = 0
        self.dealer_hole_card_revealed = False

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

    # === Game State ===
    def reset_hands(self):
        """Prepare a fresh round while keeping the current shoe."""
        self.player.hand = Hand()
        self.player.split_hands = []
        self.player.split_bets = []
        self.dealer_hand = Hand()
        self.dealer_hole_card_revealed = False

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

    def start_round(self):
        """Prepare the game state for a new round."""
        self.reshuffle_if_needed()
        self.reset_hands()
        self.current_bet = self.display.input_bet(self.player.credits)
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

    def _compare_hands(self):
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
        result = self._compare_hands()
        self._update_hand_result(result, self.player.current_bet)
        self.display.display_credits(self.player.credits)
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

    # === Basic Strategy Hints ===
    def _format_double_hint(self, fallback_action):
        """Return the right hint text for a recommended double-down spot."""
        if self.can_double_down():
            return "double"
        return f"double if allowed, otherwise {fallback_action}"

    def _hint_soft_hand(self, player_total, dealer_card):
        """Strategy hinting for soft totals with two cards."""
        if player_total in {13, 14} and dealer_card in {5, 6}:
            return self._format_double_hint("hit")
        if player_total in {15, 16} and dealer_card in {4, 5, 6}:
            return self._format_double_hint("hit")
        if player_total == 17 and dealer_card in {3, 4, 5, 6}:
            return self._format_double_hint("hit")
        if player_total == 18:
            if dealer_card in {3, 4, 5, 6}:
                return self._format_double_hint("stand")
            if dealer_card in {2, 7, 8}:
                return "stand"
            return "hit"
        if player_total in {19, 20, 21}:
            return "stand"
        return "hit"

    def _hint_hard_hand_double(self, player_total, dealer_card):
        """Strategy hinting for hard hand doubling with two cards."""
        if player_total == 9 and dealer_card in {3, 4, 5, 6}:
            return self._format_double_hint("hit")
        if player_total == 10 and dealer_card in {2, 3, 4, 5, 6, 7, 8, 9}:
            return self._format_double_hint("hit")
        if player_total == 11 and dealer_card != 11:
            return self._format_double_hint("hit")
        return None

    def _hint_hard_general(self, player_total, dealer_card):
        """Strategy hinting for general hard hand play."""
        if player_total >= 17:
            return "stand"
        if player_total >= 13:
            return "stand" if dealer_card in {2, 3, 4, 5, 6} else "hit"
        if player_total == 12:
            return "stand" if dealer_card in {4, 5, 6} else "hit"
        return "hit"

    def hint_action_basic_strategy(self):
        """Return a basic-strategy hint including common double-down spots."""
        player_total = self.player.hand.value()
        dealer_card = self.get_dealer_visible_value()
        is_soft_total = self.player.hand.is_soft()

        if is_soft_total and len(self.player.hand.cards) == 2:
            return self._hint_soft_hand(player_total, dealer_card)

        if len(self.player.hand.cards) == 2:
            hint = self._hint_hard_hand_double(player_total, dealer_card)
            if hint:
                return hint

        return self._hint_hard_general(player_total, dealer_card)

    # === Round Flow ===
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
            hand_length = len(self.player.hand.cards)
            action = self.display.input_action(hand_length, self.can_double_down(), self.can_split())

            if action == "hit":
                self.display.clear_screen()
                self.display.animate_deal(self.deal_card, self.player.hand, lambda: self.get_table_state("Player Hits"))

                if self.player.hand.is_busted():
                    self.player.lost_bet(self.player.current_bet)
                    self.count_dealer_hidden_card()
                    self.show_result("Round Result", "Player busted! Dealer wins.", "red")
                    return True
                if self.player.hand.value() == 21:
                    self.display.print_colored("\nPlayer reached 21 and stands automatically.", "yellow", bold=True)
                    return False
            elif action == "stand":
                self.display.print_colored("\nPlayer stands.", "yellow", bold=True)
                return False
            elif action == "double" and self.can_double_down():
                self.player.place_bet(self.player.current_bet * 2)
                self.display.clear_screen()
                self.display.animate_deal(self.deal_card, self.player.hand, lambda: self.get_table_state("Player Doubles and Stands"))
                if self.player.hand.is_busted():
                    self.player.lost_bet(self.player.current_bet)
                    self.count_dealer_hidden_card()
                    self.show_result("Round Result", "Player busted! Dealer wins.", "red")
                    return True
                if self.player.hand.value() == 21:
                    self.display.print_colored("\nPlayer doubled to 21 and stands automatically.", "yellow", bold=True)
                return False
            elif action == "split" and self.can_split():
                self.split_hand()
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

    def split_hand(self):
        """Handle splitting the player's hand when two initial cards are the same rank."""
        self.player.split_hand()

        for i, hand in enumerate(self.player.split_hands):
            self.player.hand = hand
            self.display.clear_screen()
            self.display.animate_deal(
                self.deal_card,
                self.player.hand,
                lambda i=i: self.get_table_state(f"Dealing card to Hand {i + 1}"),
            )

        for i, hand in enumerate(self.player.split_hands):
            self.player.hand = hand
            self.display.clear_screen()
            self.display.display_table(
                **self.get_table_state(f">>> PLAYING HAND {i + 1} of {len(self.player.split_hands)} <<<")
            )
            self.display.print_colored(f"\n=== HAND {i + 1} ===", "cyan", bold=True)
            self.handle_player_turn()

        self.player.hand = self.player.split_hands[0]

    # === Result Display ===
    def get_result_color(self, result):
        """Return display color based on game result."""
        if "Player wins" in result:
            return "green"
        if "Dealer wins" in result or "busted" in result:
            return "red"
        return "yellow"

    def _display_result_section(self, result_text, color):
        """Display a formatted result section with dividers."""
        self.display.print_colored("", "green", bold=True)
        self.display.print_divider()
        self.display.print_colored(result_text, color, bold=True)
        self.display.print_divider()

    def show_result(self, title, message, color):
        """Render a final round state and its result message."""
        self.display.display_table(**self.get_table_state(title, reveal_dealer=True))
        self._display_result_section(message, color)

    def show_final_result(self):
        """Display the final hands and winner."""
        if self.player.has_split():
            self._show_split_hand_results()
        else:
            self._show_single_hand_result()

    def _show_split_hand_results(self):
        """Display results for each split hand."""
        for i, hand in enumerate(self.player.split_hands):
            self.player.hand = hand
            hand_bet = self.player.split_bets[i]
            self.display.clear_screen()
            self.display.display_table(
                **self.get_table_state(f">>> FINAL HAND {i + 1} of {len(self.player.split_hands)} <<<", reveal_dealer=True)
            )
            result = self._compare_hands()
            self._update_hand_result(result, hand_bet)

            self.display.display_credits(self.player.credits)
            result_color = self.get_result_color(result)
            self._display_result_section(f"HAND {i + 1}: {result}", result_color)

        self.player.hand = self.player.split_hands[0]

    def _show_single_hand_result(self):
        """Display result for a single non-split hand."""
        self.display.display_table(**self.get_table_state("Final Hands", reveal_dealer=True))
        result = self.determine_winner()
        result_color = self.get_result_color(result)
        self._display_result_section(result, result_color)

    def _update_hand_result(self, result, hand_bet):
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
