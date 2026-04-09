import pygame
import random

# =============================
# Constants and Globals
# =============================
BACKGROUND_COLOR = (30, 92, 58)
RANKS = ['2','3','4','5','6','7','8','9','10','jack','queen','king','ace']
SUITS = ['hearts','diamonds','clubs','spades']
CARD_WIDTH = 100
CARD_HEIGHT = 150

card_images = {}

# =============================
# Load Card Images
# =============================
def load_card_images():
    for rank in RANKS:
        for suit in SUITS:
            key = f"{rank}_of_{suit}"
            img = pygame.image.load(f"cards/{key}.png")
            img = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
            card_images[key] = img

def draw_card_image(screen, card, x, y):
    image = card_images.get(f"{card.rank}_of_{card.suit}")
    if image:
        screen.blit(image, (x, y))

# =============================
# Card Class
# =============================
class Card:
    def __init__(self, rank, suit):
        self.rank = rank 
        self.suit = suit 
        self.value = self.get_value()
    
    def get_value(self):
        if self.rank in ['jack', 'queen', 'king']: 
            return 10
        elif self.rank == 'ace': 
            return 11
        else:
            return int(self.rank)
        
# =============================
# Blackjack Game Class
# =============================
class BlackjackGame:
    def __init__(self):
        self.reset()

    def deal_card(self, hand):
        card = self.deck.pop()
        hand.append(card)


    def calculate_hand_value(self, hand):
        total = sum(card.value for card in hand)
        aces = sum(1 for card in hand if card.rank == 'ace')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total
    
# Dealer must hit until they reach 17 or higher
    def dealer_play(self):
        while self.calculate_hand_value(self.dealer_hand) < 17:
            self.deal_card(self.dealer_hand)


    def check_winner(self):
        player_total = self.calculate_hand_value(self.player_hand)
        dealer_total = self.calculate_hand_value(self.dealer_hand)

        if player_total > 21:
            return "Dealer wins! Player busts."
        elif dealer_total > 21:
            return "Player wins! Dealer busts."
        elif player_total > dealer_total:
            return "Player wins!"
        elif dealer_total > player_total:
            return "Dealer wins!"
        else:
            return "It's a tie! Push."

    def reset(self):
        self.deck = [Card(rank, suit) for rank in RANKS for suit in SUITS]
        random.shuffle(self.deck)
        self.player_hand = []
        self.dealer_hand = []


# =============================
# INPUT HANDLER
# =============================
def handle_input(event, game, state):
    if event.type == pygame.KEYDOWN:

        if event.key == pygame.K_n:
            game.reset()
            game.deal_card(game.player_hand) # Player gets first card
            game.deal_card(game.player_hand) # Player gets second card
            game.deal_card(game.dealer_hand) # Dealer gets first card (second card is hidden until player stands)
            game.deal_card(game.dealer_hand) # Dealer gets second card
            state["player_turn"] = True
            state["message"] = ""

        elif event.key == pygame.K_h and state["player_turn"]:
            game.deal_card(game.player_hand)
            # Check for bust after hit
            if game.calculate_hand_value(game.player_hand) > 21:
                state["player_turn"] = False
                state["message"] = game.check_winner()

        elif event.key == pygame.K_s and state["player_turn"]:
            state["player_turn"] = False
            game.dealer_play()
            state["message"] = game.check_winner()


# =============================
# DRAW FUNCTION
# =============================
def draw(screen, game, font, state):
    screen.fill(BACKGROUND_COLOR)

    screen.blit(font.render("N = New Game", True, (255,255,255)), (20,20))
    screen.blit(font.render("H = Hit | S = Stand", True, (255,255,255)), (20,50))

    # Display result message
    if state["message"]:
        screen.blit(font.render(state["message"], True, (255,255,0)), (20,80))

    if game:
        # Player cards
        for i, card in enumerate(game.player_hand):
            draw_card_image(screen, card, 100 + i * 120, 350)

        # Dealer cards
        for i, card in enumerate(game.dealer_hand):
            if i == 1 and state["player_turn"]:
                # pygame.draw.rect(screen, (0,0,0), (100 + i * 120, 100, CARD_WIDTH, CARD_HEIGHT)) # Hide second dealer card
                card_images["red_joker.png"] = pygame.image.load("cards/red_joker.png")
                card_images["red_joker.png"] = pygame.transform.scale(card_images["red_joker.png"], (CARD_WIDTH, CARD_HEIGHT))
                screen.blit(card_images["red_joker.png"], (100 + i * 120, 100))
            else:
                draw_card_image(screen, card, 100 + i * 120, 100)


# =============================
# MAIN
# =============================
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Blackjack")

load_card_images()

font = pygame.font.SysFont(None, 24)

game = BlackjackGame()

# game state dictionary (clean way to track things)
state = {
    "player_turn": True,
    "message": ""
}

running = True
while running:

    # ===== INPUT =====
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        handle_input(event, game, state)

    # ===== DRAW =====
    draw(screen, game, font, state)

    pygame.display.flip()

pygame.quit()