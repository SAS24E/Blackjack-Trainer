from blackjack import BlackjackGame
from display import Display
from player import Player


# Program entry point
def main():
    display = Display() 
    while True:
        player_name = input(display.colorize("Enter your name: ", "cyan", bold=True)).strip()
        if player_name:
            break
        display.print_colored("Name cannot be empty.", "red", bold=True)

    player = Player(player_name)
    player.load_from_file(player.file_name)  
    game = BlackjackGame(display, player)

    while True:
        if game.player.credits < 0.5:
            display.print_colored("\nYou are out of credits. Game over!", "red", bold=True)
            break

        game.play_game()
        game.player.save_to_file(game.player.file_name)
        play_again = input(display.colorize("\nDo you want to play again? (y/n): ", "orange", bold=True)).lower()
        if play_again != "y":
            display.print_colored("Thanks for playing!", "cyan", bold=True)
            break


if __name__ == "__main__":
    main()
