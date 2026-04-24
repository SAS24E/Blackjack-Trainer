import os
import subprocess
import sys
import time


class TerminalUI:
    """Terminal rendering and input helpers."""

    # === Constants ===
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

    # === Initialization ===
    def __init__(self):
        self.use_color = self.enable_ansi_colors()

    def enable_ansi_colors(self):
        if os.name == "nt":
            os.system("")
        return sys.stdout.isatty()

    # === Text Formatting & Styling ===
    def colorize(self, text, color_key, bold=False):
        if not self.use_color:
            return text

        color_code = self.COLORS.get(color_key, "")
        bold_code = self.COLORS["bold"] if bold else ""
        return f"{bold_code}{color_code}{text}{self.COLORS['reset']}"

    def print_colored(self, text, color_key, bold=False):
        print(self.colorize(text, color_key, bold))

    def format_amount(self, amount):
        """Format credits and bets without trailing .0 values."""
        if amount is None:
            return ""
        if float(amount).is_integer():
            return str(int(amount))
        return f"{amount:.1f}"

    # === User Input ===
    def input_action(self, hand_length, can_double=False, can_split=False):
        """Prompt the player for an action and validate it."""
        if hand_length == 2 and can_split:
            actions = {
                "1": "hit",
                "2": "stand",
                "3": "split",
                "4": "double" if can_double else "hint",
                "5": "hint" if can_double else None,
            }
            actions = {k: v for k, v in actions.items() if v is not None}
            if can_double:
                prompt = self.colorize("\nAction:: [1] Hit [2] Stand [3] Split [4] Double [5] Hint: ", "yellow", bold=True)
            else:
                prompt = self.colorize("\nAction:: [1] Hit [2] Stand [3] Split [4] Hint: ", "yellow", bold=True)
        elif hand_length == 2 and can_double:
            actions = {
                "1": "hit",
                "2": "stand",
                "3": "double",
                "4": "hint",
            }
            prompt = self.colorize("\nAction:: [1] Hit [2] Stand [3] Double [4] Hint: ", "yellow", bold=True)
        else:
            actions = {
                "1": "hit",
                "2": "stand",
                "3": "hint",
            }
            prompt = self.colorize("\nAction:: [1] Hit [2] Stand [3] Hint: ", "yellow", bold=True)
        while True:
            choice = input(prompt).strip()
            if choice in actions:
                return actions[choice]
            self.print_colored("Invalid input. Please enter a valid option.", "red", bold=True)

    def input_bet(self, available_credits):
        """Prompt for a bet in whole- or half-credit increments."""
        while True:
            prompt = self.colorize(
                f"\nEnter bet amount (available: {self.format_amount(available_credits)}): ",
                "yellow",
                bold=True,
            )
            raw_value = input(prompt).strip()

            try:
                bet_amount = float(raw_value)
            except ValueError:
                self.print_colored("Invalid bet. Enter a whole number or a value ending in .5.", "red", bold=True)
                continue

            if bet_amount <= 0:
                self.print_colored("Bet must be greater than zero.", "red", bold=True)
                continue
            if not (bet_amount * 2).is_integer():
                self.print_colored("Bet must be in whole- or half-credit increments.", "red", bold=True)
                continue
            if bet_amount > available_credits:
                self.print_colored("Bet cannot exceed available credits.", "red", bold=True)
                continue

            return int(bet_amount) if bet_amount.is_integer() else bet_amount

    # === Game Rendering ===
    def render_table(
        self,
        title,
        player_hand,
        dealer_hand,
        reveal_dealer=False,
        running_count=0,
        dealer_upcard_value=0,
        player_credits=None,
    ):
        """Render the current table state."""
        print()
        self.print_divider()
        self.print_colored(title, "cyan", bold=True)
        self.print_divider()

        self.print_colored(f"Running Count: {running_count}", "cyan", bold=True)

        self.print_colored("Dealer:", "magenta", bold=True)
        self.render_graphical_hand(dealer_hand, hide_dealer_card=not reveal_dealer)
        if reveal_dealer:
            self.print_colored(f"\nDealer total: {dealer_hand.value()}", "yellow", bold=True)
        else:
            self.print_colored(f"\nDealer showing: {dealer_upcard_value}", "yellow", bold=True)

        self.print_colored("\nPlayer:", "green", bold=True)
        self.render_graphical_hand(player_hand)
        self.print_colored(f"\nPlayer total: {player_hand.value()}", "yellow", bold=True)
        self.render_credits(player_credits)
        self.print_divider()

    def render_graphical_hand(self, hand, hide_dealer_card=False):
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

    def render_credits(self, credits=None):
        """Display credits when provided by the game state."""
        if credits is None:
            return
        self.print_colored(f"Credits: {self.format_amount(credits)}", "green", bold=True)

    def animate_deal(self, deal_card_func, hand, table_state_getter):
        """Deal a card and render the updated table as one animation frame."""
        deal_card_func(hand)
        self.clear_screen()
        self.render_table(**table_state_getter())
        sys.stdout.flush()
        time.sleep(0.5)

    # === Terminal Helpers ===
    def clear_screen(self):
        """Clear the terminal screen."""
        command = "cls" if os.name == "nt" else "clear"
        subprocess.run(command, shell=True)

    def print_divider(self):
        print(self.colorize("=" * 34, "cyan"))
