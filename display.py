import os
import sys

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
    