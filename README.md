# Blackjack Trainer

A command-line Blackjack game in Python with card counting (Hi-Lo system), basic strategy hints, split hand support, and player persistence.

## Features

- ✅ Full Blackjack rules: hit, stand, double down, split hands
- ✅ Card counting with running count display
- ✅ Basic strategy hints for optimal play
- ✅ Auto-stand at 21
- ✅ Player stats and credits saved between sessions

## Project Structure

```
blackjack-trainer/
├── main.py              # Entry point
├── blackjack.py         # Game engine and rules
├── player.py            # Player state and betting
├── hand.py              # Hand evaluation
├── card.py              # Card representation
├── deck.py              # Deck management
├── display.py           # Terminal UI
├── {player}_data.txt    # Saved player stats
└── README.md
```

## Installation

```bash
python3 main.py
```

No external dependencies required.

## How to Play

1. Enter your name
2. Place a bet (whole or half-credit increments)
3. Choose an action:
   - **[1] Hit**: Take another card
   - **[2] Stand**: Keep your hand
   - **[3] Double**: Double bet, get one card (2-card hands only)
   - **[4] Split**: Split matching cards into two hands
   - **[5] Hint**: Get basic strategy recommendation

## Game Rules

- **Objective**: Get closer to 21 than dealer without busting
- **Card Values**: 2-10 = face value, J/Q/K = 10, Ace = 11 or 1
- **Blackjack**: 21 on first 2 cards (pays 1.5x)
- **Push**: Tie with dealer (return bet)
- **Bust**: Over 21 (lose bet)
- **Dealer Rules**: Hits on 16 or lower, stands on 17+

## File Descriptions

| File           | Purpose                                     |
| -------------- | ------------------------------------------- |
| `main.py`      | CLI entry point and game loop               |
| `blackjack.py` | Core game logic, rules, strategy hints      |
| `player.py`    | Player state, betting, statistics, file I/O |
| `hand.py`      | Hand value calculation and evaluation       |
| `card.py`      | Card definition (rank, suit, value)         |
| `deck.py`      | Deck creation and card dealing              |
| `display.py`   | Terminal UI (colors, ASCII cards, prompts)  |

## Author
Stephen Secor

Built as a final project for CIS4930 - Python Course at Florida State University
