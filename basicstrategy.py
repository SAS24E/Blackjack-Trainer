
class BasicStrategy:
    """Basic strategy hinting for the current blackjack game state."""

    def __init__(self, game):
        self.game = game

    @property
    def player(self):
        return self.game.player

    # === Basic Strategy Hints ===
    def format_double_hint(self, fallback_action):
        """Return the right hint text for a recommended double-down spot."""
        if self.game.can_double_down():
            return "double"
        return f"double if allowed, otherwise {fallback_action}"

    def hint_soft_hand(self, player_total, dealer_card):
        """Strategy hinting for soft totals with two cards."""
        if player_total in {13, 14} and dealer_card in {5, 6}:
            return self.format_double_hint("hit")
        if player_total in {15, 16} and dealer_card in {4, 5, 6}:
            return self.format_double_hint("hit")
        if player_total == 17 and dealer_card in {3, 4, 5, 6}:
            return self.format_double_hint("hit")
        if player_total == 18:
            if dealer_card in {3, 4, 5, 6}:
                return self.format_double_hint("stand")
            if dealer_card in {2, 7, 8}:
                return "stand"
            return "hit"
        if player_total in {19, 20, 21}:
            return "stand"
        return "hit"

    def hint_hard_hand_double(self, player_total, dealer_card):
        """Strategy hinting for hard hand doubling with two cards."""
        if player_total == 9 and dealer_card in {3, 4, 5, 6}:
            return self.format_double_hint("hit")
        if player_total == 10 and dealer_card in {2, 3, 4, 5, 6, 7, 8, 9}:
            return self.format_double_hint("hit")
        if player_total == 11 and dealer_card != 11:
            return self.format_double_hint("hit")
        return None

    def hint_hard_general(self, player_total, dealer_card):
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
        dealer_card = self.game.dealer_upcard_value()
        is_soft_total = self.player.hand.is_soft()

        if is_soft_total and len(self.player.hand.cards) == 2:
            return self.hint_soft_hand(player_total, dealer_card)

        if len(self.player.hand.cards) == 2:
            hint = self.hint_hard_hand_double(player_total, dealer_card)
            if hint:
                return hint

        return self.hint_hard_general(player_total, dealer_card)
