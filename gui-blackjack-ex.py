import random
import pygame

WIDTH, HEIGHT = 800, 600
WHITE, BLACK, GREEN, RED = (255, 255, 255), (0, 0, 0), (34, 139, 34), (255, 0, 0)

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def build_deck():
    """Build and shuffle a 52-card deck."""
    deck = [(r, s) for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

def card_value(card):
    """Get blackjack value of a card."""
    rank = card[0]
    if rank in ["J", "Q", "K"]:
        return 10
    if rank == "A":
        return 11
    return int(rank)

def calculate_score(cards):
    """Calculate best score, adjusting for Aces."""
    score = sum(card_value(c) for c in cards)
    aces = sum(1 for c in cards if c[0] == "A")
    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score

def get_message(player_score, dealer_score):
    """Get result message."""
    if player_score > 21:
        return "BUST! You lose."
    if dealer_score > 21:
        return "Dealer busts! You win!"
    if player_score == dealer_score:
        return "PUSH (tie)."
    if player_score > dealer_score:
        return "You win!"
    return "Dealer wins."


# -----------------------------
# UI classes
# -----------------------------
class Button:
    def __init__(self, rect, text, color, hover_color=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color if hover_color else color

    def draw(self, surface, font, mouse_pos):
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if is_hovered else self.color

        pygame.draw.rect(surface, (0, 0, 0), self.rect.move(4, 4), border_radius=14)
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=14)

        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class ChipButton:
    def __init__(self, center, value, color):
        self.center = center
        self.value = value
        self.color = color
        self.radius = 28

    def draw(self, surface, font, mouse_pos):
        mx, my = mouse_pos
        hovered = (mx - self.center[0]) ** 2 + (my - self.center[1]) ** 2 <= self.radius ** 2
        r = self.radius + 3 if hovered else self.radius

        pygame.draw.circle(surface, BLACK, (self.center[0] + 3, self.center[1] + 3), r)
        pygame.draw.circle(surface, self.color, self.center, r)
        pygame.draw.circle(surface, WHITE, self.center, r, 3)
        pygame.draw.circle(surface, WHITE, self.center, r - 8, 2)

        txt = font.render(f"${self.value}", True, WHITE)
        txt_rect = txt.get_rect(center=self.center)
        surface.blit(txt, txt_rect)

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            return (mx - self.center[0]) ** 2 + (my - self.center[1]) ** 2 <= self.radius ** 2
        return False


class AnimatedCard:
    def __init__(self, card, start_pos, target_pos, face_up=True, duration=18):
        self.card = card
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.face_up = face_up
        self.duration = duration
        self.frame = 0
        self.done = False

    def update(self):
        self.frame += 1
        if self.frame >= self.duration:
            self.frame = self.duration
            self.done = True

    def get_pos(self):
        t = self.frame / self.duration
        x = eased_lerp(self.start_pos[0], self.target_pos[0], t)
        y = eased_lerp(self.start_pos[1], self.target_pos[1], t)
        return int(x), int(y)


# -----------------------------
# Main game class
# -----------------------------
class BlackjackGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Blackjack Deluxe")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_xl = pygame.font.SysFont("arial", 42, bold=True)
        self.font_lg = pygame.font.SysFont("arial", 30, bold=True)
        self.font_md = pygame.font.SysFont("arial", 24, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 18, bold=True)

        self.hit_button = Button((930, 610, 120, 55), "HIT", BUTTON_GREEN, (55, 175, 85))
        self.stand_button = Button((1070, 610, 140, 55), "STAND", BUTTON_RED, (190, 75, 75))
        self.new_button = Button((930, 675, 280, 55), "NEW ROUND", BUTTON_BLUE, (85, 130, 230))

        self.chip_buttons = [
            ChipButton((955, 520), 5, (200, 60, 60)),
            ChipButton((1025, 520), 10, (60, 100, 210)),
            ChipButton((1095, 520), 25, (50, 145, 80)),
            ChipButton((1165, 520), 50, (120, 60, 150)),
        ]

        self.balance = 250
        self.bet = 10

        self.reset_round()

    # -----------------------------------------
    # Round setup
    # -----------------------------------------
    def reset_round(self):
        self.deck = build_deck()
        self.player_cards = []
        self.dealer_cards = []
        self.animations = []
        self.dealing_queue = []
        self.game_over = False
        self.player_turn = False
        self.show_dealer_hidden = False
        self.message = "Place your bet and play."
        self.round_started = False
        self.result_paid = False

        if self.balance <= 0:
            self.balance = 250
            self.message = "Bankroll reset to $250."

        if self.bet > self.balance:
            self.bet = max(5, self.balance)

        self.start_round()

    def start_round(self):
        self.round_started = True
        self.player_cards.clear()
        self.dealer_cards.clear()
        self.animations.clear()
        self.dealing_queue.clear()
        self.game_over = False
        self.player_turn = False
        self.show_dealer_hidden = False
        self.result_paid = False
        self.message = "Dealing cards..."

        # queue initial four cards
        self.queue_deal("player", True)
        self.queue_deal("dealer", True)
        self.queue_deal("player", True)
        self.queue_deal("dealer", False)

    def queue_deal(self, owner, face_up=True):
        card = self.deck.pop()
        if owner == "player":
            index = len(self.player_cards)
            target = (160 + index * (CARD_W + CARD_GAP), 515)
        else:
            index = len(self.dealer_cards)
            target = (160 + index * (CARD_W + CARD_GAP), 170)

        self.dealing_queue.append((owner, card, face_up, target))

    def begin_next_animation(self):
        if self.animations or not self.dealing_queue:
            return

        owner, card, face_up, target = self.dealing_queue.pop(0)

        if owner == "player":
            self.player_cards.append(card)
        else:
            self.dealer_cards.append(card)

        start_pos = (WIDTH // 2 - CARD_W // 2, 40)
        self.animations.append(AnimatedCard(card, start_pos, target, face_up=face_up))

    # -----------------------------------------
    # Turn logic
    # -----------------------------------------
    def player_hit(self):
        if self.game_over or not self.player_turn:
            return
        self.queue_deal("player", True)
        self.message = "You hit."
        self.player_turn = False

    def dealer_turn(self):
        self.show_dealer_hidden = True
        dealer_score = calculate_score(self.dealer_cards)

        while dealer_score != 0 and dealer_score < 17:
            self.queue_deal("dealer", True)
            dealer_score = calculate_score(self.dealer_cards)

    def finish_round(self):
        self.game_over = True
        self.show_dealer_hidden = True

        player_score = calculate_score(self.player_cards)
        dealer_score = calculate_score(self.dealer_cards)
        self.message = compare(player_score, dealer_score)

        if not self.result_paid:
            if player_score == 0 and dealer_score != 0:
                self.balance += int(self.bet * 1.5)
            elif dealer_score > 21 or (player_score <= 21 and (player_score > dealer_score or dealer_score == 0 and player_score != 0)):
                self.balance += self.bet
            elif player_score == dealer_score:
                pass
            else:
                self.balance -= self.bet
            self.result_paid = True

    # -----------------------------------------
    # Event handling
    # -----------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_h:
                    self.player_hit()
                if event.key == pygame.K_s and self.player_turn and not self.game_over:
                    self.message = "Dealer's turn..."
                    self.player_turn = False
                    self.dealer_turn()
                if event.key == pygame.K_n:
                    self.reset_round()

            if self.hit_button.clicked(event):
                self.player_hit()

            if self.stand_button.clicked(event) and self.player_turn and not self.game_over:
                self.message = "Dealer's turn..."
                self.player_turn = False
                self.dealer_turn()

            if self.new_button.clicked(event):
                self.reset_round()

            if not self.round_started or self.game_over:
                for chip in self.chip_buttons:
                    if chip.clicked(event):
                        if chip.value <= self.balance:
                            self.bet = chip.value
                            self.message = f"Bet set to ${self.bet}"

        return True

    # -----------------------------------------
    # Update
    # -----------------------------------------
    def update(self):
        if not self.animations:
            self.begin_next_animation()

        for anim in self.animations[:]:
            anim.update()
            if anim.done:
                self.animations.remove(anim)

                # after initial deal, let player act unless blackjack/bust
                if not self.dealing_queue and not self.game_over:
                    player_score = calculate_score(self.player_cards)
                    dealer_score = calculate_score(self.dealer_cards)

                    if len(self.player_cards) >= 2 and len(self.dealer_cards) >= 2 and not self.player_turn:
                        if player_score == 0 or dealer_score == 0:
                            self.finish_round()
                        elif player_score > 21:
                            self.finish_round()
                        elif self.show_dealer_hidden and not self.dealing_queue:
                            # dealer was playing
                            dealer_score = calculate_score(self.dealer_cards)
                            if dealer_score >= 17 or dealer_score > 21:
                                self.finish_round()
                        else:
                            self.player_turn = True
                            self.message = "Your turn: Hit or Stand."

        # if dealer queued cards but no current animation, continue
        if not self.animations and self.dealing_queue:
            self.begin_next_animation()

        # if player busted after hit animation
        if not self.animations and not self.dealing_queue and not self.game_over:
            player_score = calculate_score(self.player_cards)
            if player_score > 21:
                self.finish_round()
            elif self.show_dealer_hidden and not self.player_turn:
                dealer_score = calculate_score(self.dealer_cards)
                if dealer_score >= 17 or dealer_score > 21:
                    self.finish_round()
                else:
                    self.dealer_turn()

    # -----------------------------------------
    # Drawing helpers
    # -----------------------------------------
    def draw_background(self):
        self.screen.fill(TABLE_DARK)

        # table shadow
        shadow_rect = pygame.Rect(58, 88, 1160, 620)
        pygame.draw.ellipse(self.screen, (0, 0, 0), shadow_rect)

        # felt table
        table_rect = pygame.Rect(50, 80, 1160, 620)
        pygame.draw.ellipse(self.screen, TABLE_GREEN, table_rect)
        pygame.draw.ellipse(self.screen, TABLE_LINE, table_rect, 4)

        # inner arc/details
        pygame.draw.arc(self.screen, TABLE_LINE, (180, 430, 520, 180), math.radians(200), math.radians(340), 3)
        pygame.draw.arc(self.screen, TABLE_LINE, (575, 430, 520, 180), math.radians(200), math.radians(340), 3)

        title = self.font_xl.render("BLACKJACK DELUXE", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 42)))

        subtitle = self.font_sm.render("Dealer must stand on 17", True, WHITE)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 75)))

    def draw_panel(self):
        panel = pygame.Rect(900, 120, 335, 620)
        pygame.draw.rect(self.screen, (20, 25, 30), panel, border_radius=24)
        pygame.draw.rect(self.screen, GOLD, panel, width=2, border_radius=24)

        bal = self.font_lg.render(f"Bankroll: ${self.balance}", True, WHITE)
        bet = self.font_lg.render(f"Current Bet: ${self.bet}", True, WHITE)

        self.screen.blit(bal, (925, 155))
        self.screen.blit(bet, (925, 195))

        choose = self.font_md.render("Choose Bet", True, GOLD)
        self.screen.blit(choose, (925, 255))

        info_lines = [
            "Controls:",
            "H = Hit",
            "S = Stand",
            "N = New Round",
        ]
        y = 325
        for line in info_lines:
            surf = self.font_sm.render(line, True, WHITE)
            self.screen.blit(surf, (925, y))
            y += 28

        msg_title = self.font_md.render("Table Message", True, GOLD)
        self.screen.blit(msg_title, (925, 395))

        wrapped = self.wrap_text(self.message, self.font_sm, 280)
        y = 432
        for line in wrapped:
            surf = self.font_sm.render(line, True, WHITE)
            self.screen.blit(surf, (925, y))
            y += 24

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    def draw_score_labels(self):
        dealer_text = self.font_lg.render("DEALER", True, WHITE)
        player_text = self.font_lg.render("PLAYER", True, WHITE)
        self.screen.blit(dealer_text, (165, 125))
        self.screen.blit(player_text, (165, 470))

        if self.show_dealer_hidden or self.game_over:
            dealer_score = calculate_score(self.dealer_cards)
            dealer_score_display = 21 if dealer_score == 0 else dealer_score
            dealer_score_txt = self.font_md.render(f"Score: {dealer_score_display}", True, WHITE)
        else:
            first_value = card_value(self.dealer_cards[0]) if self.dealer_cards else 0
            dealer_score_txt = self.font_md.render(f"Showing: {first_value}", True, WHITE)

        player_score = calculate_score(self.player_cards)
        player_score_display = 21 if player_score == 0 else player_score
        player_score_txt = self.font_md.render(f"Score: {player_score_display}", True, WHITE)

        self.screen.blit(dealer_score_txt, (300, 130))
        self.screen.blit(player_score_txt, (300, 475))

    def draw_card(self, x, y, card, face_up=True):
        card_rect = pygame.Rect(x, y, CARD_W, CARD_H)

        # shadow
        pygame.draw.rect(self.screen, (0, 0, 0), card_rect.move(4, 4), border_radius=10)

        if not face_up:
            pygame.draw.rect(self.screen, (25, 55, 130), card_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, card_rect, 3, border_radius=10)

            for i in range(6):
                pygame.draw.line(
                    self.screen,
                    (210, 220, 255),
                    (x + 10, y + 15 + i * 18),
                    (x + CARD_W - 10, y + 15 + i * 18),
                    2,
                )
            inner = pygame.Rect(x + 18, y + 18, CARD_W - 36, CARD_H - 36)
            pygame.draw.rect(self.screen, (35, 80, 180), inner, 2, border_radius=8)
            return

        pygame.draw.rect(self.screen, WHITE, card_rect, border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, card_rect, 2, border_radius=10)

        rank, suit = card
        color = SUIT_COLORS[suit]

        small = self.font_sm.render(rank, True, color)
        small_suit = self.font_sm.render(suit, True, color)
        big = self.font_lg.render(suit, True, color)

        self.screen.blit(small, (x + 8, y + 6))
        self.screen.blit(small_suit, (x + 10, y + 26))

        center_rect = big.get_rect(center=(x + CARD_W // 2, y + CARD_H // 2))
        self.screen.blit(big, center_rect)

        # bottom-right rotated feel without actual rotation
        br_rank = self.font_sm.render(rank, True, color)
        br_suit = self.font_sm.render(suit, True, color)
        self.screen.blit(br_rank, (x + CARD_W - 22 - br_rank.get_width(), y + CARD_H - 42))
        self.screen.blit(br_suit, (x + CARD_W - 22 - br_suit.get_width(), y + CARD_H - 22))

    def draw_hands(self):
        # dealer
        for i, card in enumerate(self.dealer_cards):
            x = 160 + i * (CARD_W + CARD_GAP)
            y = 170
            face_up = True
            if i == 1 and not self.show_dealer_hidden and not self.game_over:
                face_up = False
            self.draw_card(x, y, card, face_up)

        # player
        for i, card in enumerate(self.player_cards):
            x = 160 + i * (CARD_W + CARD_GAP)
            y = 515
            self.draw_card(x, y, card, True)

        # animated cards on top
        for anim in self.animations:
            pos = anim.get_pos()
            self.draw_card(pos[0], pos[1], anim.card, anim.face_up)

    def draw_bet_circle(self):
        center = (650, 560)
        pygame.draw.circle(self.screen, TABLE_LINE, center, 72, 3)
        pygame.draw.circle(self.screen, (0, 0, 0), (center[0] + 4, center[1] + 4), 62)
        pygame.draw.circle(self.screen, (140, 30, 30), center, 62)
        pygame.draw.circle(self.screen, GOLD, center, 62, 3)

        bet_text = self.font_lg.render(f"${self.bet}", True, WHITE)
        self.screen.blit(bet_text, bet_text.get_rect(center=center))

    def draw_controls(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hit_button.draw(self.screen, self.font_md, mouse_pos)
        self.stand_button.draw(self.screen, self.font_md, mouse_pos)
        self.new_button.draw(self.screen, self.font_md, mouse_pos)

        if not self.game_over:
            for chip in self.chip_buttons:
                chip.draw(self.screen, self.font_sm, mouse_pos)

    def draw_footer_hint(self):
        hint = "Tip: Use the mouse or press H / S / N"
        surf = self.font_sm.render(hint, True, WHITE)
        self.screen.blit(surf, (40, HEIGHT - 34))

    def draw(self):
        self.draw_background()
        self.draw_panel()
        self.draw_score_labels()
        self.draw_hands()
        self.draw_bet_circle()
        self.draw_controls()
        self.draw_footer_hint()
        pygame.display.flip()

    # -----------------------------------------
    # Main loop
    # -----------------------------------------
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# -----------------------------
# Program entry point
# -----------------------------
if __name__ == "__main__":
    game = BlackjackGame()
    game.run()