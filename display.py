import os
import subprocess
import sys
import time

class Display:
    """Terminal rendering and input helpers."""

    # Display constants
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "cyan": "\033[36m",
        "yellow": "\033[33m",
        "green": "\033[32m",
        "red": "\033[31m",
        "magenta": "\033[35m",
        "orange": "\033[38;5;208m",
    }

    RANK_SYMBOLS = {
        "ace": "A",
        "king": "K",
        "queen": "Q",
        "jack": "J",
    }

    # Setup
    def __init__(self):
        self.use_color = self._enable_ansi_colors()

    # Input and animation
    def animate_deal(self, deal_card_func, hand, table_state_getter):
        """Deal a card and render the updated table as one animation frame."""
        deal_card_func(hand)
        self.clear_screen()
        self.display_table(**table_state_getter())
        sys.stdout.flush()
        time.sleep(0.5)

    def colorize(self, text, color_key, bold=False):
        if not self.use_color:
            return text

        color_code = self.COLORS.get(color_key, "")
        bold_code = self.COLORS["bold"] if bold else ""
        return f"{bold_code}{color_code}{text}{self.COLORS['reset']}"

    def print_colored(self, text, color_key, bold=False):
        print(self.colorize(text, color_key, bold))

    def input_action(self):
        """Prompt the player for an action and validate it."""
        actions = {
            "1": "hit",
            "2": "stand",
            "3": "hint",
        }

        while True:
            prompt = self.colorize("\nAction [1] Hit [2] Stand [3] Hint: ", "yellow", bold=True)
            choice = input(prompt).strip()
            if choice in actions:
                return actions[choice]
            self.print_colored("Invalid input. Please enter 1, 2, or 3.", "red", bold=True)

    def input_bet(self, available_credits):
        """Prompt for a numeric bet that does not exceed available credits."""
        while True:
            prompt = self.colorize(
                f"\nEnter bet amount (available: {available_credits}): ",
                "yellow",
                bold=True,
            )
            raw_value = input(prompt).strip()

            if not raw_value.isdigit():
                self.print_colored("Invalid bet. Enter a whole number.", "red", bold=True)
                continue

            bet_amount = int(raw_value)
            if bet_amount <= 0:
                self.print_colored("Bet must be greater than zero.", "red", bold=True)
                continue
            if bet_amount > available_credits:
                self.print_colored("Bet cannot exceed available credits.", "red", bold=True)
                continue

            return bet_amount

    # Table rendering
    def display_graphical_hand(self, hand, hide_dealer_card=False):
        """Render a hand as ASCII playing cards."""
        card_height = 7
        card_lines = [[] for _ in range(card_height)]

        for index, card in enumerate(hand.cards):
            if hide_dealer_card and index == 1:
                card_art = [
                    "┌───────┐",
                    "│*******│",
                    "│*******│",
                    "│*******│",
                    "│*******│",
                    "│*******│",
                    "└───────┘",
                ]
                color = "magenta"
            else:
                rank_text = self.RANK_SYMBOLS.get(card.rank, card.rank)
                card_art = [
                    "┌───────┐",
                    f"│ {rank_text:<2}    │",
                    "│       │",
                    f"│   {card.suit[0].upper()}   │",
                    "│       │",
                    f"│    {rank_text:>2} │",
                    "└───────┘",
                ]
                color = "red" if card.suit.lower() in {"hearts", "diamonds"} else "cyan"

            for i, line in enumerate(card_art):
                card_lines[i].append(self.colorize(line, color, bold=True))

        for line in card_lines:
            print("  ".join(line))

    def display_table(
        self,
        title,
        player_hand,
        dealer_hand,
        reveal_dealer=False,
        running_count=0,
        dealer_visible_value=0,
        player_credits=None,
    ):
        """Render the current table state."""
        print()
        self.print_divider()
        self.print_colored(title, "cyan", bold=True)
        self.print_divider()

        self.print_colored(f"Running Count: {running_count}", "cyan", bold=True)

        self.print_colored("Dealer:", "magenta", bold=True)
        self.display_graphical_hand(dealer_hand, hide_dealer_card=not reveal_dealer)
        if reveal_dealer:
            self.print_colored(f"\nDealer total: {dealer_hand.value()}", "yellow", bold=True)
        else:
            self.print_colored(f"\nDealer showing: {dealer_visible_value}", "yellow", bold=True)

        self.print_colored("\nPlayer:", "green", bold=True)
        self.display_graphical_hand(player_hand)
        self.print_colored(f"\nPlayer total: {player_hand.value()}", "yellow", bold=True)
        self.display_credits(player_credits)
        self.print_divider()

    # Terminal helpers
    def _enable_ansi_colors(self):
        if os.name == "nt":
            os.system("")
        return sys.stdout.isatty()

    def print_divider(self):
        print(self.colorize("=" * 34, "cyan"))

    def clear_screen(self):
        """Clear the terminal screen."""
        command = "cls" if os.name == "nt" else "clear"
        subprocess.run(command, shell=True)

    def display_credits(self, credits=None):
        """Display credits when provided by the game state."""
        if credits is None:
            return
        self.print_colored(f"Credits: {credits}", "green", bold=True)
