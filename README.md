# Blackjack Trainer

A command-line Blackjack game in Python with betting, card counting, basic strategy hints, split hand support, and player save data.

## Features

- Blackjack actions: hit, stand, double down, and split
- Whole-number betting
- Hi-Lo running count display
- Basic strategy hints
- Automatic stand at 21
- Player credits and stats saved between sessions

## How to Run

```bash
python main.py
```

No external dependencies are required.

## How to Play

1. Enter your name.
2. Place a whole-number bet.
3. Choose an action during your turn:
   - `[1] Hit`: take another card
   - `[2] Stand`: keep your current hand
   - `[3] Double`: double your bet, take one card, then stand
   - `[4] Split`: split a matching pair into two hands
   - `Hint`: get a basic strategy recommendation when shown as an option
4. After the round, your credits and stats are saved automatically.

## Game Rules

- The goal is to get closer to 21 than the dealer without busting.
- Number cards are worth their face value.
- Jack, queen, and king are worth 10.
- Ace is worth 11 or 1, whichever works best for the hand.
- Blackjack is a two-card 21 and pays 1.5x.
- Push means a tie with the dealer.
- Dealer hits on 16 or lower and stands on 17 or higher.

## Project Structure

```text
blackjack-trainer/
|-- main.py            # Program entry point
|-- blackjack.py       # Main game flow and blackjack rules
|-- basicstrategy.py   # Basic strategy hint logic
|-- player.py          # Player credits, bets, stats, and save data
|-- hand.py            # Hand value calculation
|-- card.py            # Card representation
|-- deck.py            # Deck creation and card dealing
|-- display.py         # Terminal UI, prompts, and table display
|-- *_data.txt         # Saved player data
`-- README.md
```

## File Descriptions

| File | Purpose |
| --- | --- |
| `main.py` | Starts the program and controls replay/save flow |
| `blackjack.py` | Runs rounds, handles actions, dealer play, results, splits, and card counting |
| `basicstrategy.py` | Provides hint recommendations based on the player's hand and dealer upcard |
| `player.py` | Stores player state, credits, bets, split hands, and save/load logic |
| `hand.py` | Calculates hand totals, soft hands, busts, and blackjack |
| `card.py` | Defines card ranks, suits, and card values |
| `deck.py` | Builds, shuffles, and deals cards |
| `display.py` | Handles terminal colors, user input, and card/table rendering |

## Author

Alex Secor


