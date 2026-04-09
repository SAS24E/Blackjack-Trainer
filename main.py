from blackjack import BlackjackGame
from display import Display


# Program entry point
def main():
    display = Display()
    game = BlackjackGame(display)

    while True:
        game.play_game()
        play_again = input(display.colorize("\nDo you want to play again? (y/n): ", "orange", bold=True)).lower()
        if play_again != "y":
            display.print_colored("Thanks for playing!", "cyan", bold=True)
            break


if __name__ == "__main__":
    main()
