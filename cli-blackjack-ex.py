# Graphical Blackjack Game in Python
# The goal of the game is to get as close to 21 as possible without going over
# Each player starts with two cards and can choose to "hit" (get another card) or "stand" (keep their current hand)

import pygame
import sys
import random

# Game logic functions
def deal_card():
    """Returns a random card from the deck."""
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    return random.choice(cards)

def calculate_score(cards):
    """Calculates the score of the given cards."""
    # Make a copy to avoid modifying the original list
    cards_copy = cards.copy()
    if sum(cards_copy) == 21 and len(cards_copy) == 2:
        return 0  # Blackjack
    if 11 in cards_copy and sum(cards_copy) > 21:
        cards_copy.remove(11)
        cards_copy.append(1)
    return sum(cards_copy)

def compare(user_score, computer_score):
    """Compares the user's score with the computer's score and returns the result."""
    if user_score == computer_score:
        return "Draw"
    elif computer_score == 0:
        return "Lose, opponent has Blackjack"
    elif user_score == 0:
        return "Win with a Blackjack"
    elif user_score > 21:
        return "You went over. You lose"
    elif computer_score > 21:
        return "Opponent went over. You win"
    elif user_score > computer_score:
        return "You win"
    else:
        return "You lose"

class BlackjackGame:
    def __init__(self):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Blackjack Game")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        self.reset_game()
        
    def reset_game(self):
        """Initialize a new game."""
        self.user_cards = [deal_card(), deal_card()]
        self.computer_cards = [deal_card(), deal_card()]
        self.user_score = calculate_score(self.user_cards)
        self.computer_score = calculate_score(self.computer_cards)
        self.game_over = False
        self.message = ""
        self.show_computer_hand = False
        
    def handle_events(self):
        """Handle user input and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_h:  # Hit
                        self.user_cards.append(deal_card())
                        self.user_score = calculate_score(self.user_cards)
                        if self.user_score > 21:
                            self.end_game()
                    elif event.key == pygame.K_s:  # Stand
                        self.dealer_turn()
                        self.end_game()
                elif event.key == pygame.K_n:  # New game
                    self.reset_game()
        return True
    
    def dealer_turn(self):
        """Let the dealer play their turn."""
        while self.computer_score != 0 and self.computer_score < 17:
            self.computer_cards.append(deal_card())
            self.computer_score = calculate_score(self.computer_cards)
        self.show_computer_hand = True
    
    def end_game(self):
        """End the game and show result."""
        if not self.show_computer_hand:
            self.dealer_turn()
        self.game_over = True
        self.message = compare(self.user_score, self.computer_score)
    
    def draw(self):
        """Draw the game on the screen."""
        self.screen.fill((0, 100, 0))  # Green background
        
        # Draw dealer's hand
        dealer_label = self.font_medium.render("Dealer's Hand", True, (255, 255, 255))
        self.screen.blit(dealer_label, (50, 50))
        
        if self.show_computer_hand:
            for i, card in enumerate(self.computer_cards):
                card_text = self.font_large.render(str(card), True, (255, 0, 0))
                self.screen.blit(card_text, (50 + i * 80, 100))
            dealer_score_text = self.font_medium.render(f"Score: {self.computer_score}", True, (255, 255, 255))
            self.screen.blit(dealer_score_text, (50, 160))
        else:
            card_text = self.font_large.render(str(self.computer_cards[0]), True, (255, 0, 0))
            self.screen.blit(card_text, (50, 100))
            hidden_text = self.font_large.render("?", True, (255, 0, 0))
            self.screen.blit(hidden_text, (130, 100))
        
        # Draw player's hand
        player_label = self.font_medium.render("Your Hand", True, (255, 255, 255))
        self.screen.blit(player_label, (50, 300))
        
        for i, card in enumerate(self.user_cards):
            card_text = self.font_large.render(str(card), True, (0, 255, 0))
            self.screen.blit(card_text, (50 + i * 80, 350))
        
        player_score_text = self.font_medium.render(f"Score: {self.user_score}", True, (255, 255, 255))
        self.screen.blit(player_score_text, (50, 420))
        
        # Draw buttons/instructions
        if not self.game_over:
            hit_text = self.font_small.render("Press 'H' to Hit or 'S' to Stand", True, (255, 255, 0))
        else:
            hit_text = self.font_small.render("Press 'N' for New Game", True, (255, 255, 0))
        self.screen.blit(hit_text, (50, 480))
        
        # Draw result message
        if self.game_over:
            result_text = self.font_large.render(self.message, True, (255, 255, 255))
            self.screen.blit(result_text, (150, 530))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = BlackjackGame()
    game.run()

