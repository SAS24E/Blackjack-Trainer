from blackjack import BlackjackGame
from display import TerminalUI
from player import Player


# Program entry point
def main():
    ui = TerminalUI()
    ui.welcome_message()
    while True:
        player_name = input(ui.colorize("Enter your name: ", "cyan", bold=True)).strip()
        if player_name:
            break
        ui.print_colored("Name cannot be empty.", "red", bold=True)

    player = Player(player_name)
    player.load_from_file(player.file_name)  
    game = BlackjackGame(ui, player)
    ui.display_user_stats(player.wins, player.losses, player.ties, player)

    while True:
        if game.player.credits < 0.5:
            ui.print_colored("\nYou are out of credits. Game over!", "red", bold=True)
            ui.display_user_stats(game.player.wins, game.player.losses, game.player.ties, game.player)
            ui.exit_message()
            break

        game.play_game()
        game.player.save_to_file(game.player.file_name)
        play_again = input(ui.colorize("\nDo you want to play again? (y/n): ", "orange", bold=True)).lower()
        if play_again != "y":
            ui.exit_message()
            ui.display_user_stats(game.player.wins, game.player.losses, game.player.ties, game.player)
            break


if __name__ == "__main__":
    main()
